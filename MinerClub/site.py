import hashlib

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import click

from .emailer import make_activation_email, send_register_email, send_registration_alert_email
from .config import Product, Messages
from .mccontrol import get_mj_id, update_whitelist
from .membership import is_member

app = Flask(__name__)
app.config.from_object(Product)

db = SQLAlchemy(app)
mail = Mail(app)


class Member(db.Model):
    id = db.Column(db.String, primary_key=True)
    sponsor_code = db.Column(db.String)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sponsor_code = self.make_code()

    @property
    def quota(self):
        return app.config['QUOTA'] - len(self.users)

    def make_code(self):
        sha = hashlib.sha256()
        sha.update(app.config['CODE_HASH'])
        sha.update(self.id.encode())
        return sha.hexdigest()

    @property
    def email(self):
        return app.config['EMAIL_TEMPLATE'].format(self.id)


class Whitelist(db.Model):
    username = db.Column(db.String, primary_key=True)
    id = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'),
                          nullable=False)
    sponsor = db.relationship('Member',
                              backref=db.backref('users', lazy=True))

    @classmethod
    def serialise(cls):
        entries = cls.query.all()
        return [entry.to_dict() for entry in entries]

    def to_dict(self):
        return {'uuid': "{}{}{}{}{}{}{}{}-{}{}{}{}-{}{}{}{}-{}{}{}{}-{}{}{}{}{}{}{}{}{}{}{}{}".format(*self.id),
                'name': self.username}


@app.route('/')
def home():
    return render_template('home.html', title='Home', club_name=app.config['CLUB_NAME'])


@app.route('/activate', methods=['POST', 'GET'])
def activate():
    if request.method == 'POST':
        member_id = request.form.get('member_id')

        if request.form.get('code') != app.config['ACCESS_CODE']:
            return render_template("message.html", bad=Messages.WRONG_ACCESS_CODE)

        if not is_member(member_id):
            return render_template("message.html", bad=Messages.WRONG_MEMBER_ID)

        if Member.query.get(member_id) is not None:
            return render_template("message.html", bad=Messages.ALREADY_ACTIVATED)

        u = Member(id=member_id)
        db.session.add(u)

        mail.send(make_activation_email(u))

        db.session.commit()

        return render_template("message.html", good=Messages.ACTIVATE_SUCCESS.format(email=u.email))

    return render_template("activate.html", title='Activate')


@app.route('/register', methods=['GET', 'POST'])
def register():
    sponsor_code = request.args.get('sponsor_code', '')
    if request.method == 'POST':
        sponsor_code, username, email = (request.form.get('sponsor_code'),
                                        request.form.get('username'),
                                        request.form.get('email'))

        sponsor = Member.query.filter_by(sponsor_code=sponsor_code.strip()).first()

        if sponsor is None:
            return render_template("message.html", bad=Messages.WRONG_SPONSOR_CODE)

        if sponsor.quota < 1:
            return render_template("message.html", bad=Messages.OUTTA_GUESTS)

        mj_id = get_mj_id(username)

        if mj_id is None:
            return render_template("message.html", bad=Messages.UNKNOWN_USERNAME)

        if Whitelist.query.get(username):
            return render_template("message.html", bad=Messages.ALREADY_WHITELISTED)

        w = Whitelist(username=username, sponsor=sponsor, id=mj_id, email=email)
        db.session.add(w)

        mail.send(send_register_email(w))
        mail.send(send_registration_alert_email(w))

        db.session.commit()
        update_whitelist(Whitelist)

        return render_template("message.html", good=Messages.REGISTER_SUCCESS.format(email=email))

    return render_template("register.html", sponsor_code=sponsor_code, title='Register')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html', title='Privacy Policy', club_name=app.config['CLUB_NAME'])


@app.cli.command("init")
def init_db():
    click.echo("Creating database")
    db.create_all()
    click.echo("Committing change")
    db.session.commit()
    click.echo("Success")


@app.cli.command("reset-db")
def reset_db():
    click.echo("Dropping all tables")
    db.drop_all()
    db.session.commit()
    click.echo("Recreating them")
    db.create_all()
    db.session.commit()
    click.echo("Success")


@app.cli.command("force-sync")
def force_sync():
    click.echo("Forcing whitelist sync")
    update_whitelist(Whitelist)
    click.echo("Success")
