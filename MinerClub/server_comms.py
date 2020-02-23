import json
import datetime
import os
from abc import abstractmethod
from pathlib import Path
from io import BytesIO
import shutil

from ftplib import FTP_TLS, FTP
from ftputil import FTPHost, session
import pysftp

from flask import current_app


class FileManager():
    engines = {}
    host = None

    @property
    def engine_name(self):
        return current_app.config['FILE_ENGINE']

    @property
    def engine(self):
        return self.engines[self.engine_name]

    def __getattr__(self, item):
        return getattr(self.engine, item)

    @classmethod
    def add_engine(cls, name):
        def wraps(new_class):
            cls.engines[name] = new_class()
            new_class.ENGINE = name
            return new_class

        return wraps


class AbstractFileEngine:
    ENGINE = None

    @property
    def address(self):
        return current_app.config['{}_SERVER_ADDRESS'.format(self.ENGINE)]

    @property
    def port(self):
        return current_app.config['{}_SERVER_PORT'.format(self.ENGINE)]

    @property
    def username(self):
        return current_app.config['{}_SERVER_USERNAME'.format(self.ENGINE)]

    @property
    def password(self):
        return current_app.config['{}_SERVER_PASSWORD'.format(self.ENGINE)]

    @property
    def whitelist(self):
        return current_app.config['{}_WHITELIST_PATH'.format(self.ENGINE)]

    @abstractmethod
    def get_host(self):
        """
        Get an instance of some connection-like hosty thing that is used to communicate with the filesystem of the
        server.

        It needs to be usable as a context manager. Whereby entering establishes a connection that is used for
        operations for that session.
        """
        pass

    @abstractmethod
    def write_text(self, host, path, text):
        """
        Write text to path on the filesystem of the server.
        """
        pass

    def copy_dir(self, host, source, destination):
        raise NotImplementedError("copy_dir needs to be implemented with {} for backups")

    @abstractmethod
    def listdir(self, host, path):
        raise NotImplementedError("listdir needs to be implemented with {} for automated testing")

    @abstractmethod
    def walk(self, host, path):
        raise NotImplementedError("listdir needs to be implemented with {} for automated testing")

    @abstractmethod
    def read_text(self, host, path):
        raise NotImplementedError("listdir needs to be implemented with {} for automated testing")


@FileManager.add_engine('FTP')
class FTPFileEngine(AbstractFileEngine):

    def get_host(self):
        c = current_app.config
        my_session_factory = session.session_factory(base_class=FTP, port=c['FTP_SERVER_PORT'])
        return FTPHost(c['FTP_SERVER_ADDRESS'],
                       c['FTP_SERVER_USERNAME'],
                       c['FTP_SERVER_PASSWORD'],
                       session_factory=my_session_factory)

    def write_text(self, host, path, text):
        with host.open(path, 'w') as f:
            f.write(text)

    def read_text(self, host, path):
        with host.open(path) as f:
            return f.read()

    def listdir(self, host, path):
        return host.listdir(path)

    def walk(self, host, path):
        return host.walk(path)

    def copy_dir(self, host, source, destination):
        from_ = Path(source)
        to = Path(destination)
        for root, dirs, files in host.walk(from_.as_posix()):
            root = Path(root)
            dest_dir = to / root.relative_to(
                from_.parent)  # if from_ is a subdirectory, no point having full path there

            if not dest_dir.exists():
                dest_dir.mkdir()

            for file in files:
                source = root / file
                destination = dest_dir / file
                host.download(source.as_posix(), destination.as_posix())


@FileManager.add_engine('FTPS')
class FTPSFileEngine(FTPFileEngine):

    def get_host(self):
        c = current_app.config
        my_session_factory = session.session_factory(base_class=FTP_TLS,
                                                     use_passive_mode=True,
                                                     port=c['FTPS_SERVER_PORT'],
                                                     encrypt_data_channel=True)
        return FTPHost(c['FTPS_SERVER_ADDRESS'],
                       c['FTPS_SERVER_USERNAME'],
                       c['FTPS_SERVER_PASSWORD'],
                       session_factory=my_session_factory)


@FileManager.add_engine('SFTP')
class SFTPFileManager(AbstractFileEngine):

    def get_host(self):
        c = current_app.config
        cnopts = pysftp.CnOpts()
        if not current_app.config['SFTP_HOSTKEY_CHECK']:
            cnopts.hostkeys = None
        return pysftp.Connection(host=c['SFTP_SERVER_ADDRESS'],
                                 username=c['SFTP_SERVER_USERNAME'],
                                 password=c['SFTP_SERVER_PASSWORD'],
                                 port=c['SFTP_SERVER_PORT'],
                                 cnopts=cnopts)

    def write_text(self, host, path, text):
        host.putfo(BytesIO(text.encode()), path)

    def read_text(self, host, path):
        buffer = BytesIO()
        host.getfo(path, buffer)
        return buffer.getvalue().decode('utf-8')

    def listdir(self, host, path):
        return host.listdir(path)

    def walk(self, host, path):
        files = []
        dirs = [Path(path)]
        host.walktree(path,
                      fcallback=lambda p: files.append(Path(p)),
                      dcallback=lambda d: dirs.append(Path(d)),
                      ucallback=lambda u: u)

        tree = {}

        dirs.sort(key=lambda d: len(d.parts))

        for folder in dirs:
            tree[folder] = [[], []]

        dirs.pop(0)

        for folder in dirs:
            tree[folder.parent][0].append(folder.name)

        for file in files:
            tree[file.parent][1].append(file.name)

        for root, (folders, files) in tree.items():
            yield root, folders, files

    def copy_dir(self, host, source, destination):

        from_ = Path(source)
        to = Path(destination)
        for root, dirs, files in self.walk(host, from_.as_posix()):
            root = Path(root)
            dest_dir = to / root.relative_to(
                from_.parent)  # if from_ is a subdirectory, no point having full path there

            if not dest_dir.exists():
                dest_dir.mkdir()

            for file in files:
                source = root / file
                destination = dest_dir / file
                host.get(source.as_posix(), destination.as_posix())


@FileManager.add_engine('LOCAL')
class LocalFileEngine(AbstractFileEngine):

    @property
    def home(self):
        return Path(current_app.config['LOCAL_SERVER_DIR'])

    def get_host(self):
        return self

    def write_text(self, host, path, text):
        (self.home / path).write_text(text)

    def copy_dir(self, host, source, destination):
        source = self.home / source
        # needed as shutil.copytree copies source contents, not top level folder!
        destination = destination / source.parts[-1]
        shutil.copytree(source.as_posix(), destination.as_posix())

    def listdir(self, host, path):
        return os.listdir(self.home / path)

    def walk(self, host, path):
        return os.walk(self.home / path)

    def read_text(self, host, path):
        return (self.home / path).read_text()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


file_manager = FileManager()


def update_whitelist(whitelist):
    data = whitelist.serialise()
    with file_manager.get_host() as host:
        file_manager.write_text(host, file_manager.whitelist, json.dumps(data, indent=4))


def get_now():
    return datetime.datetime.now().strftime(current_app.config['BACKUP_DIR_FORMAT'])


def outdated_backups():
    backups = []
    for item in os.scandir(current_app.config['BACKUP_DESTINATION']):
        if not item.is_dir():
            continue
        try:
            date = datetime.datetime.strptime(item.name, current_app.config['BACKUP_DIR_FORMAT'])
            backups.append((date, item))
        except ValueError as e:
            continue

    backups.sort(key=lambda backup: backup[0])

    rotation = current_app.config['BACKUP_ROTATION'] - 1 # because I'll make a new one!

    if len(backups) > rotation:
        index = None if rotation == 0 else -rotation # because :0 is different to :None.
        return backups[:index]
    else:
        return []
