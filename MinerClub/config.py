import os
import pathlib
import tempfile

from dotenv import load_dotenv
load_dotenv()


class Required:
    pass


def to_bool(val):
    return val in ('True', 'true', '1')
 

class Base:
    FLASK_DEBUG: bool = None

    # Site setup
    CLUB_NAME: str = Required
    SERVER_IP: str = Required
    ACCESS_CODE: str = Required
    QUOTA: int = 4
    CODE_SALT: bytes = Required
    USE_MEMBERS_LIST: bool = True
    EMAIL_TEMPLATE: str = '{}'
    ADMIN_NAME: str = ''
    ADMIN_EMAIL: str = ''
    DISCORD_URL: str = ''

    # File setup
    FILE_ENGINE: str = 'SFTP'

    FTP_WHITELIST_PATH: str = 'whitelist.json'
    FTP_SERVER_ADDRESS: str = Required
    FTP_SERVER_USERNAME: str = Required
    FTP_SERVER_PASSWORD: str = Required
    FTP_SERVER_PORT: int = 21

    FTPS_WHITELIST_PATH: str = 'whitelist.json'
    FTPS_SERVER_ADDRESS: str = Required
    FTPS_SERVER_USERNAME: str = Required
    FTPS_SERVER_PASSWORD: str = Required
    FTPS_SERVER_PORT: int = 21

    SFTP_WHITELIST_PATH: str = 'whitelist.json'
    SFTP_SERVER_ADDRESS: str = Required
    SFTP_SERVER_USERNAME: str = Required
    SFTP_SERVER_PASSWORD: str = Required
    SFTP_SERVER_PORT: int = 22
    SFTP_HOSTKEY_CHECK: bool = True
    
    LOCAL_SERVER_DIR: str = Required
    LOCAL_WHITELIST_PATH: str = 'whitelist.json'

    # Backup setup
    BACKUP_SOURCES: list = ['world', 'world_the_end', 'world_nether']
    BACKUP_DESTINATION: str = 'backups'
    BACKUP_DIR_FORMAT: str = '%y-%m-%d_(%Hh%Mm)'
    BACKUP_ROTATION: int = 3

    # Mail setup
    MAIL_SERVER: str = Required
    MAIL_PORT: int = 587
    MAIL_USE_TLS: bool = True
    MAIL_USERNAME: str = Required
    MAIL_SENDER: tuple = Required
    MAIL_PASSWORD: str = Required

    # Database setup
    DATABASE_FILE: str = 'database.db'
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///" + DATABASE_FILE
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


def from_env(key, post=lambda v: v):
    try:
        return post(os.environ[key])
    except KeyError:
        default = getattr(Base, key)
        if default is Required:
            raise ValueError(f"Required config value {key} not set")
        return default


def get_config(config):
    if config == 'product':
        class ProductConfig(Base):
            TESTING = False
            FLASK_DEBUG = False

            # Site setup
            CLUB_NAME = from_env('CLUB_NAME')
            SERVER_IP = from_env('SERVER_IP')
            ACCESS_CODE = from_env('ACCESS_CODE')
            QUOTA = from_env('QUOTA', post=int)
            CODE_SALT = from_env('CODE_SALT', lambda v: v.encode())
            USE_MEMBERS_LIST = from_env('USE_MEMBERS_LIST', to_bool)
            EMAIL_TEMPLATE = from_env('EMAIL_TEMPLATE')
            ADMIN_NAME = from_env('ADMIN_NAME')
            ADMIN_EMAIL = from_env('ADMIN_EMAIL')
            DISCORD_URL = from_env('DISCORD_URL')

            # File setup
            FILE_ENGINE = from_env('FILE_ENGINE')

            if FILE_ENGINE == 'FTP':
                FTP_WHITELIST_PATH = from_env('FTP_WHITELIST_PATH')
                FTP_SERVER_ADDRESS = from_env('FTP_SERVER_ADDRESS')
                FTP_SERVER_USERNAME = from_env('FTP_SERVER_USERNAME')
                FTP_SERVER_PASSWORD = from_env('FTP_SERVER_PASSWORD')
                FTP_SERVER_PORT = from_env('FTP_SERVER_PORT', int)

            if FILE_ENGINE == 'FTPS':
                FTPS_WHITELIST_PATH = from_env('FTPS_WHITELIST_PATH')
                FTPS_SERVER_ADDRESS = from_env('FTPS_SERVER_ADDRESS')
                FTPS_SERVER_USERNAME = from_env('FTPS_SERVER_USERNAME')
                FTPS_SERVER_PASSWORD = from_env('FTPS_SERVER_PASSWORD')
                FTPS_SERVER_PORT = from_env('FTPS_SERVER_PORT', int)

            if FILE_ENGINE == 'SFTP':
                SFTP_WHITELIST_PATH = from_env('SFTP_WHITELIST_PATH')
                SFTP_SERVER_ADDRESS = from_env('SFTP_SERVER_ADDRESS')
                SFTP_SERVER_USERNAME = from_env('SFTP_SERVER_USERNAME')
                SFTP_SERVER_PASSWORD = from_env('SFTP_SERVER_PASSWORD')
                SFTP_SERVER_PORT = from_env('SFTP_SERVER_PORT', int)
                SFTP_HOSTKEY_CHECK = from_env('SFTP_HOSTKEY_CHECK', to_bool)

            if FILE_ENGINE == 'LOCAL':
                LOCAL_SERVER_DIR = from_env('LOCAL_SERVER_DIR')
                LOCAL_WHITELIST_PATH = from_env('LOCAL_WHITELIST_PATH')

            # Backup setup
            BACKUP_SOURCES = from_env('BACKUP_SOURCES', lambda v: v.split(','))
            BACKUP_DESTINATION = from_env('BACKUP_DESTINATION')
            BACKUP_DIR_FORMAT = from_env('BACKUP_DIR_FORMAT')
            BACKUP_ROTATION = from_env('BACKUP_ROTATION', int)

            # Mail setup
            MAIL_SERVER = from_env('MAIL_SERVER')
            MAIL_PORT = from_env('MAIL_PORT', int)
            MAIL_USE_TLS = from_env('MAIL_USE_TLS', to_bool)
            MAIL_USERNAME = from_env('MAIL_USERNAME')
            MAIL_SENDER = (CLUB_NAME, MAIL_SERVER)
            MAIL_PASSWORD = from_env('MAIL_PASSWORD')

            # Database setup
            DATABASE_FILE = from_env('DATABASE_FILE')
            SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_FILE
        return ProductConfig

    elif config == 'testing':

        class TestingConfig(Base):
            TESTING = True
            FLASK_DEBUG = True

            CLUB_NAME = "Testing Club"
            SERVER_IP = "127.0.0.1"
            ACCESS_CODE = ""
            CODE_SALT = "Testing Salt".encode()

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
            LOCAL_SERVER_DIR = None

            BACKUP_SOURCES = "basedir,basedir/subdir".split(',')
            BACKUP_DESTINATION = None
            BACKUP_ROTATION = 1
            BACKUP_DIR_FORMAT = 'Testing Backup'

            MAIL_SERVER = "127.0.0.1"
            MAIL_USERNAME = "Test Username"
            MAIL_SENDER = (f"Testing {CLUB_NAME}", MAIL_USERNAME)
            MAIL_PASSWORD = "Test Password"

            DATABASE_FILE = pathlib.Path(tempfile.gettempdir()) / "database.db"
            SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_FILE.as_posix()

        return TestingConfig


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

    ACTIVATION_SUBJECT = '{CLUB_NAME} Activation Successful'
    REGISTRATION_SUBJECT = '{CLUB_NAME} Whitelisting Successful'
    REGISTRATION_ALERT_SUBJECT = '{CLUB_NAME} Whitelisting Registration Alert'
