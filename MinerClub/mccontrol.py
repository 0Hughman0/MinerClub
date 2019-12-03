from ftplib import FTP
import io
from pathlib import Path
import json

from flask import current_app
import requests


def get_mj_id(username):
    p = requests.post("https://api.mojang.com/profiles/minecraft", data='["{}"]'.format(username))
    if p.json():
        return p.json()[0]['id']
    else:
        return None


def write_file(filename, text):
    filename = Path(current_app.config['FTP_BASEDIR']) / filename
    ftp = FTP()
    ftp.connect(current_app.config['FTP_ADDRESS'], port=current_app.config['FTP_PORT'])
    ftp.login(user=current_app.config['FTP_USER'], passwd=current_app.config['FTP_PASSWORD'])

    for part in filename.parts[:-1]:
        ftp.cwd(part)

    ftp.storbinary('STOR ' + filename.name, io.BytesIO(text.encode()))


def read_file(filename):
    filename = Path(current_app.config['FTP_BASEDIR']) / filename
    ftp = FTP()
    ftp.connect(current_app.config['FTP_ADDRESS'])
    ftp.login(user=current_app.config['FTP_USER'], passwd=current_app.config['FTP_PASSWORD'])

    for part in filename.parts[:-1]:
        ftp.cwd(part)

    stream = io.BytesIO()
    ftp.retrbinary('RETR ' + filename.name, stream.write)

    return stream.getvalue().decode('utf-8')


def update_whitelist(whitelist):
    data = whitelist.serialise()
    write_file(current_app.config['WHITELIST_FILE'], json.dumps(data, indent=4))
