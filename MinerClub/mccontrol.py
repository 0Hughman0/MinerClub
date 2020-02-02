import datetime
from pathlib import Path
import json
from ftplib import FTP, FTP_TLS

from flask import current_app
import requests
from ftputil import FTPHost


def get_host():
    c = current_app.config
    session_factory = FTP_TLS if c['FTP_USE_TLS'] else FTP
    return FTPHost(c['FTP_ADDRESS'], c['FTP_USERNAME'], c['FTP_PASSWORD'], session_factory=session_factory)


def get_now():
    return datetime.datetime.now().strftime(current_app.config['BACKUP_DIR_FORMAT'])


def get_mj_id(username):
    p = requests.post("https://api.mojang.com/profiles/minecraft", data='["{}"]'.format(username))
    if p.json():
        return p.json()[0]['id']
    else:
        return None


def write_file(filename, text):
    with get_host() as host:
        with host.open(filename, 'w') as f:
            f.write(text)


def read_file(filename):
    with get_host() as host:
        with host.open(filename) as f:
            return f.read()


def copy_dir(from_, to):
    from_ = Path(from_)
    to = Path(to)
    with get_host() as host:
        for root, dirs, files in host.walk(from_.as_posix()):
            root = Path(root)
            dest_dir = to / root.relative_to(from_.parent) # if from_ is a subdirectory, no point having full path there

            if not dest_dir.exists():
                dest_dir.mkdir()

            for file in files:
                source = root / file
                destination = dest_dir / file
                host.download(source.as_posix(), destination.as_posix())


def update_whitelist(whitelist):
    data = whitelist.serialise()
    write_file(current_app.config['FTP_WHITELIST_PATH'], json.dumps(data, indent=4))
