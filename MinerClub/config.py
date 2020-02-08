import os
import pathlib
import tempfile

from dotenv import load_dotenv
load_dotenv()


def to_bool(val):
    return val in ('True', 'true', '1')


class Base:
    FLASK_DEBUG = False

    # Site setup
    CLUB_NAME = os.environ['CLUB_NAME']
    SERVER_IP = os.environ['SERVER_IP']
    ACCESS_CODE = os.environ['ACCESS_CODE']
    QUOTA = int(os.environ.get('QUOTA', '4'))
    CODE_SALT = os.environ['CODE_SALT'].encode()
    EMAIL_TEMPLATE = os.environ.get('EMAIL_TEMPLATE', '{}')
    ADMIN_NAME = os.environ.get('ADMIN_NAME')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    DISCORD_URL = os.environ.get('DISCORD_URL')

    # FTP setup
    FTP_ADDRESS = os.environ['FTP_IP']
    FTP_PORT = int(os.environ.get('FTP_PORT', '21'))
    FTP_USERNAME = os.environ['FTP_USERNAME']
    FTP_PASSWORD = os.environ['FTP_PASSWORD']
    FTP_WHITELIST_PATH = os.environ.get('FTP_WHITELIST_PATH', 'whitelist.json')
    FTP_USE_TLS = to_bool(os.environ.get('FTP_USE_TLS', "False"))

    # Backup setup
    BACKUP_SOURCES = os.environ.get('BACKUP_SOURCES', 'world,world_the_end,world_nether').split(',')
    BACKUP_DESTINATION = os.environ.get('BACKUP_DESTINATION', 'backups')
    BACKUP_DIR_FORMAT = os.environ.get('BACKUP_DIR_FORMAT', '%y-%m-%d (%Hh%Mm)')
    BACKUP_ROTATION = int(os.environ.get('BACKUP_ROTATION', '3'))

    # Mail setup
    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = to_bool(os.environ.get('MAIL_USE_TLS', 'True'))
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_SENDER = (CLUB_NAME, MAIL_SERVER)
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']

    # Database setup
    DATABASE_FILE = os.environ.get('DATABASE_FILE', 'database.db')
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_FILE


class Debug(Base):
    TESTING = True
    FLASK_DEBUG = True

    DATABASE_FILE = pathlib.Path(tempfile.gettempdir()) / "database.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_FILE.as_posix()

    ACCESS_CODE = ""

    FTP_ADDRESS = "localhost"
    FTP_BASEDIR = 'basedir'
    FTP_WHITELIST_PATH = 'basedir/whitelist.json'

    BACKUP_SOURCES = "basedir,basedir/subdir".split(',')
    BACKUP_DESTINATION = None
    BACKUP_ROTATION = 1
    BACKUP_DIR_FORMAT = '%y-%m-%d (%Hh%Mm%Ss%fms)'

    MAIL_SENDER = ("Testing {}".format(Base.CLUB_NAME), Base.MAIL_USERNAME)


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
