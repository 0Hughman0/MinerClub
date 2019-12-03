from flask_mail import Message

from flask import current_app, url_for, render_template

from .config import Messages


def make_activation_email(person):
    text = render_template('activate_email.txt',
                           member_id=person.id,
                           register_url=url_for('register', sponsor_code=person.sponsor_code, _external=True),
                           quota=current_app.config['QUOTA'],
                           admin_name=current_app.config['ADMIN_NAME'],
                           admin_email=current_app.config['ADMIN_EMAIL'])
    return make_email(person.email, Messages.ACTIVATION_SUBJECT, text)


def send_register_email(whitelist_entry):
    text = render_template('registration_email.txt',
                           email=whitelist_entry.email,
                           username=whitelist_entry.username,
                           server_ip=current_app.config['SERVER_IP'],
                           discord_url=current_app.config['DISCORD_URL'],
                           admin_name=current_app.config['ADMIN_NAME'],
                           admin_email=current_app.config['ADMIN_EMAIL'])
    return make_email(whitelist_entry.email, Messages.REGISTRATION_SUBJECT, text)


def send_registration_alert_email(whitelist_entry):
    spons = whitelist_entry.sponsor
    text = render_template('registration_alert_email.txt',
                           member_id=spons.id,
                           username=whitelist_entry.username,
                           left=spons.quota,
                           users=spons.users,
                           admin_name=current_app.config['ADMIN_NAME'],
                           admin_email=current_app.config['ADMIN_EMAIL'])
    return make_email(spons.email, Messages.REGISTRATION_ALERT_SUBJECT, text)


def make_email(to, subject, text):
    msg = Message(subject,
                  sender=current_app.config['MAIL_SENDER'],
                  recipients=[to],
                  body=text)
    return msg
