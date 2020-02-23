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
    USE_MEMBERS_LIST = to_bool(os.environ.get('USER_MEMBERS_LIST', 'True'))
    EMAIL_TEMPLATE = os.environ.get('EMAIL_TEMPLATE', '{}')
    ADMIN_NAME = os.environ.get('ADMIN_NAME')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    DISCORD_URL = os.environ.get('DISCORD_URL')

    # File setup
    FILE_ENGINE = os.environ.get('FILE_ENGINE', 'FTP')

    if FILE_ENGINE == 'FTP':
        FTP_WHITELIST_PATH = os.environ.get('FILE_ENGINE_SERVER_WHITELIST_PATH', 'whitelist.json')
        FTP_SERVER_ADDRESS = os.environ['FTP_SERVER_ADDRESS']
        FTP_SERVER_USERNAME = os.environ['FTP_SERVER_USERNAME']
        FTP_SERVER_PASSWORD = os.environ['FTP_SERVER_PASSWORD']
        FTP_SERVER_PORT = int(os.environ.get('FILE_ENGINE_SERVER_PORT', '21'))

    if FILE_ENGINE == 'FTPS':
        FTPS_WHITELIST_PATH = os.environ.get('FTPS_WHITELIST_PATH', 'whitelist.json')
        FTPS_SERVER_ADDRESS = os.environ['FTPS_SERVER_ADDRESS']
        FTPS_SERVER_USERNAME = os.environ['FTPS_SERVER_USERNAME']
        FTPS_SERVER_PASSWORD = os.environ['FTPS_SERVER_PASSWORD']
        FTPS_SERVER_PORT = int(os.environ.get('FTPS_SERVER_PORT', '21'))

    if FILE_ENGINE == 'SFTP':
        SFTP_WHITELIST_PATH = os.environ.get('SFTP_WHITELIST_PATH', 'whitelist.json')
        SFTP_SERVER_ADDRESS = os.environ['SFTP_SERVER_ADDRESS']
        SFTP_SERVER_USERNAME = os.environ['SFTP_SERVER_USERNAME']
        SFTP_SERVER_PASSWORD = os.environ['SFTP_SERVER_PASSWORD']
        SFTP_SERVER_PORT = int(os.environ.get('SFTP_SERVER_PORT', '22'))
        SFTP_HOSTKEY_CHECK = to_bool(os.environ.get('SFTP_ENGINE_HOSTKEY_CHECK', 'True'))

    if FILE_ENGINE == 'LOCAL':
        LOCAL_SERVER_DIR = os.environ['LOCAL_ENGINE_SERVER_HOME']
        LOCAL_WHITELIST_PATH = os.environ.get('SFTP_WHITELIST_PATH', 'whitelist.json')

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

    FTP_SERVER_ADDRESS = '127.0.0.1'
    FTP_SERVER_WHITELIST_PATH = 'basedir/whitelist.json'
    FTP_SERVER_PORT = 21
    FTP_SERVER_USERNAME = 'FTP username'
    FTP_SERVER_PASSWORD = 'FTP test_password'

    FTPS_WHITELIST_PATH = 'basedir/whitelist.json'
    FTPS_SERVER_ADDRESS = '127.0.0.1'
    FTPS_SERVER_PORT = 21
    FTPS_SERVER_USERNAME = 'FTPS username'
    FTPS_SERVER_PASSWORD = 'FTPS test_password'

    SFTP_WHITELIST_PATH = 'basedir/whitelist.json'
    SFTP_SERVER_ADDRESS = '127.0.0.1'
    SFTP_SERVER_PORT = 22
    SFTP_HOSTKEY_CHECK = False
    SFTP_SERVER_USERNAME = 'SFTP username'
    SFTP_SERVER_PASSWORD = 'SFTP test_password'

    LOCAL_WHITELIST_PATH = 'basedir/whitelist.json'
    LOCA_SERVER_DIR = None

    BACKUP_SOURCES = "basedir,basedir/subdir".split(',')
    BACKUP_DESTINATION = None
    BACKUP_ROTATION = 1
    BACKUP_DIR_FORMAT = 'Testing Backup'

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
