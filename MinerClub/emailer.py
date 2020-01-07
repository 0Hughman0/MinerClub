from flask_mail import Message

from flask import current_app, url_for, render_template

from .config import Messages


def make_activation_email(member):
    text = render_template('activate_email.txt',
                           member=member)
    return make_email(member.email, Messages.ACTIVATION_SUBJECT, text)


def make_register_email(entry):
    text = render_template('registration_email.txt',
                           entry=entry)
    return make_email(entry.email, Messages.REGISTRATION_SUBJECT, text)


def make_registration_alert_email(entry):
    spons = entry.sponsor
    text = render_template('registration_alert_email.txt',
                           entry=entry,
                           sponsor=spons)
                           #member_id=spons.id,
                           #username=entry.username,
                           #left=spons.quota,
                           #users=spons.users,
                           #admin_name=current_app.config['ADMIN_NAME'],
                           #admin_email=current_app.config['ADMIN_EMAIL'])
    return make_email(spons.email, Messages.REGISTRATION_ALERT_SUBJECT, text)


def make_email(to, subject, text):
    msg = Message(subject,
                  sender=current_app.config['MAIL_SENDER'],
                  recipients=[to],
                  body=text)
    return msg
