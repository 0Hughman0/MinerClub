import os


class Base:
    CLUB_NAME = os.environ['CLUB_NAME']
    FLASK_DEBUG = False

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

    ACCESS_CODE = os.environ['ACCESS_CODE']
    QUOTA = int(os.environ['QUOTA'])
    CODE_HASH = os.environ['CODE_HASH'].encode()

    SERVER_IP = os.environ['SERVER_IP']

    FTP_ADDRESS = os.environ['FTP_IP']
    FTP_PORT = 21
    FTP_USER = os.environ['FTP_USER']
    FTP_PASSWORD = os.environ['FTP_PASSWORD']
    FTP_BASEDIR = os.environ['FTP_BASEDIR']
    WHITELIST_FILE = os.environ['WHITELIST_FILE']

    EMAIL_TEMPLATE = os.environ['EMAIL_TEMPLATE']

    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_SENDER = (CLUB_NAME, MAIL_SERVER)
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']

    DISCORD_URL = os.environ.get('DISCORD_URL')

    ADMIN_NAME = os.environ['ADMIN_NAME']
    ADMIN_EMAIL = os.environ['ADMIN_EMAIL']


class Debug(Base):
    TESTING = True
    FLASK_DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ACCESS_CODE = ""

    MAIL_SENDER = ("Testing {}".format(Base.CLUB_NAME), Base.MAIL_USERNAME)
    WHITELIST_FILE = 't-whitelist.json'


class Product(Base):
    TESTING = False
    FLASK_DEBUG = False


class Messages:
    WRONG_ACCESS_CODE = "Invalid Access Code."
    WRONG_MEMBER_ID = "Invalid membership ID."
    UNKNOWN_USERNAME = "Invalid Minecraft account username, please check spelling."
    ALREADY_ACTIVATED = "It seems this membership ID already has an account associated - check your inbox/ junk!"
    ACTIVATE_SUCCESS = ("Activation success! - just sent a message to {email} info on getting access to the server. "
                        "if you can't find it, check your junk!)")

    WRONG_SPONSOR_CODE = "No sponsor found with that code..."
    OUTTA_GUESTS = "Your sponsor has ran out of guests!"
    ALREADY_WHITELISTED = "This username is already added to the Whitelist."
    REGISTER_SUCCESS = ("Registration success! - Your name will be added to the whitelist and we just sent an "
                        "email to {email} with info on how to get onto the server "
                        "(if you can't find it, check your junk!)")

    ACTIVATION_SUBJECT = '{} Activation Successful'.format(Base.CLUB_NAME)
    REGISTRATION_SUBJECT = '{} Whitelisting Successful'.format(Base.CLUB_NAME)
    REGISTRATION_ALERT_SUBJECT = '{} Whitelisting Registration Alert'.format(Base.CLUB_NAME)
