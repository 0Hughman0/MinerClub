import json
import datetime
import os
from ftplib import FTP_TLS, FTP

from flask import current_app
from ftputil import FTPHost

from MinerClub.tools.ftp import write_file


def get_host():
    c = current_app.config
    session_factory = FTP_TLS if c['FTP_USE_TLS'] else FTP
    return FTPHost(c['FTP_ADDRESS'], c['FTP_USERNAME'], c['FTP_PASSWORD'], session_factory=session_factory)


def update_whitelist(whitelist):
    data = whitelist.serialise()
    with get_host() as host:
        write_file(host,current_app.config['FTP_WHITELIST_PATH'], json.dumps(data, indent=4))


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
            print(e)
            continue

    backups.sort(key=lambda backup: backup[0])

    rotation = current_app.config['BACKUP_ROTATION'] - 1 # because I'll make a new one!

    if len(backups) > rotation:
        index = None if rotation == 0 else -rotation # because :0 is different to :None.
        return backups[:index]
    else:
        return []
