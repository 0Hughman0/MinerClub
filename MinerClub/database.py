import hashlib


from flask import current_app
from flask_sqlalchemy import SQLAlchemy

from MinerClub.emailer import make_activation_email, make_register_email, make_registration_alert_email, mail

db = SQLAlchemy()


class Member(db.Model):
    id = db.Column(db.String, primary_key=True)
    sponsor_code = db.Column(db.String)
    email = db.Column(db.String)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sponsor_code = self.make_code()
        self.email = self.make_email()

    @property
    def quota(self):
        return current_app.config['QUOTA'] - len(self.users)

    def make_code(self):
        sha = hashlib.sha256()
        sha.update(current_app.config['CODE_SALT'])
        for _ in range(10):
            sha.update(self.id.encode())
        return sha.hexdigest()

    def make_email(self):
        return current_app.config['EMAIL_TEMPLATE'].format(self.id)

    def send_activate_email(self):
        mail.send(make_activation_email(self))


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

    def send_register_emails(self):
        mail.send(make_register_email(self))
        mail.send(make_registration_alert_email(self))
