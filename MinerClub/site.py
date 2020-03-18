from pathlib import Path
import shutil

from flask import Flask, render_template, request
import click

from MinerClub.database import Member, Whitelist, db

from .config import Product, Messages
from MinerClub.tools.ftp import copy_dir
from MinerClub.tools.membership import get_mj_id
from MinerClub.tools.membership import is_member
from MinerClub.emailer import mail
from MinerClub.server_comms import update_whitelist, get_now, get_host, outdated_backups

app = Flask(__name__)
app.config.from_object(Product)
db.init_app(app)
mail.init_app(app)


@app.route('/')
def home():
    return render_template('home.html', title='Home', club_name=app.config['CLUB_NAME'])


@app.route('/activate', methods=['POST', 'GET'])
def activate():
    if request.method == 'POST':
        member_id = request.form.get('member_id')

        if request.form.get('code') != app.config['ACCESS_CODE']:
            return render_template("message.html", bad=Messages.WRONG_ACCESS_CODE)

        if app.config['USE_MEMBERS_LIST'] and not is_member(member_id):
            return render_template("message.html", bad=Messages.WRONG_MEMBER_ID)

        if Member.query.get(member_id) is not None:
            return render_template("message.html", bad=Messages.ALREADY_ACTIVATED)

        u = Member(id=member_id)
        db.session.add(u)

        u.send_activate_email()

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

        w.send_register_emails()

        db.session.commit()
        update_whitelist(Whitelist)

        return render_template("message.html", good=Messages.REGISTER_SUCCESS.format(email=email))

    return render_template("register.html", sponsor_code=sponsor_code, title='Register')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html', title='Privacy Policy', club_name=app.config['CLUB_NAME'])


@app.cli.command("init", help="Initialise application database")
def init_db():
    click.echo("Creating database")
    db.create_all()
    click.echo("Committing change")
    db.session.commit()
    click.echo("Success")


@app.cli.command("reset-db", help="Wipe all database entries")
def reset_db():
    click.echo("Dropping all tables")
    db.drop_all()
    db.session.commit()
    click.echo("Recreating them")
    db.create_all()
    db.session.commit()
    click.echo("Success")


@app.cli.command("force-sync", help="Force overwriting of server whitelist with MinerClub whitelist.")
def force_sync():
    click.echo("Forcing whitelist sync")
    update_whitelist(Whitelist)
    click.echo("Success")


@app.cli.command('backup', help="Perform backup of server folders")
@click.option('--clean/--no-clean', default=False, help="Delete old backups? (defaults no)")
def backup(clean):
    if clean:
        click.echo("Cleaning up old backups")
        click.echo("Keeping roation of {} backups".format(app.config['BACKUP_ROTATION']))
        outdated = outdated_backups()
        for date, folder in outdated:
            click.echo("'{}' outdated - removing".format(folder.path, date))
            shutil.rmtree(folder.path)
            click.echo("Success")

    sources = app.config['BACKUP_SOURCES']
    destination = Path(app.config['BACKUP_DESTINATION']) / get_now()

    click.echo("Backing up {} to {}".format(sources, destination))

    click.echo("Making backup directory")
    destination.mkdir()
    click.echo("Success")
    with get_host() as host:
        for source in sources:
            sub_dest = destination / source.split('/')[-1]
            if not sub_dest.exists():
                sub_dest.mkdir()
            click.echo("Copying {}".format(source))
            copy_dir(host, source, destination)
            click.echo("Success")

    click.echo("Complete")
