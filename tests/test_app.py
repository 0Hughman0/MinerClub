import time
import json
from pathlib import Path
import os
import subprocess
import tempfile
import datetime

import pytest
from flask import render_template


from MinerClub import mail, app
from MinerClub.database import db
from MinerClub.config import Debug, Messages
from MinerClub.site import reset_db, force_sync, backup
from MinerClub.database import Member, Whitelist
from MinerClub.tools.membership import is_member
from MinerClub.tools.ftp import write_file, read_file, copy_dir
from MinerClub.server_comms import get_host, get_now, outdated_backups

app.config.from_object(Debug)
mail.init_app(app)
db.init_app(app)

test_mj_resp = [{"uuid": "f8cdb683-9e90-43ee-a819-39f85d9c5d69", "name": "mollstam"},
                {"uuid": "7125ba8b-1c86-4508-b92b-b5c042ccfe2b", "name": "KrisJelbring"}]


good_memb_code = ''
bad_memb_code = 'Wrong Code'
good_member = 'example1'
bad_member = 'Wrong member_id'

bad_sponse_code = 'Nonesense'
good_email = 'Test@email.com'

good_mc_user = test_mj_resp[0]['name']
bad_mc_user = "sdfghfdsadfghfdsaddgfhrearthgjgfd"
good_mc_user2 = test_mj_resp[1]['name']


def activate(client, code, member_id):
    return client.post('/activate',
                data={'code': code,
                      'member_id': member_id}).data.decode("utf-8")


def register(client, sponsor_code, email, username):
    return client.post('/register',
                       data={'sponsor_code': sponsor_code,
                             'email': email,
                             'username': username}).data.decode("utf-8")


@pytest.fixture
def client():
    app.config.from_object(Debug)
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.drop_all()
        db.engine.dispose()
    os.remove(app.config['DATABASE_FILE'])


@pytest.fixture
def temp_ftp():
    temp_dir = tempfile.TemporaryDirectory()
    base_dir = os.path.join(temp_dir.name, app.config['FTP_BASEDIR'])
    os.mkdir(base_dir)
    sub_dir = os.path.join(base_dir, 'subdir')
    os.mkdir(sub_dir)
    process = subprocess.Popen(['python', '-m', 'pyftpdlib',
                                '-n', '127.0.0.1',
                                '-d', temp_dir.name,
                                '-p', str(app.config['FTP_PORT']),
                                '-u', app.config['FTP_USERNAME'],
                                '-P', app.config['FTP_PASSWORD'],
                                '-w'])

    with app.app_context(), get_host() as host:
        yield process, host

    del temp_dir
    process.terminate()


def test_member():
    assert is_member(good_member) is True
    assert is_member(bad_member) is False
    assert is_member('') is False


def test_activate(client):
    resp = activate(client, bad_memb_code, good_member)
    assert resp == render_template("message.html", bad=Messages.WRONG_ACCESS_CODE)

    resp = activate(client, good_memb_code, bad_member)
    assert resp == render_template("message.html", bad=Messages.WRONG_MEMBER_ID)

    with mail.record_messages() as outbox:
        resp = activate(client, good_memb_code, good_member)

    assert resp == render_template("message.html",
                                   good=Messages.ACTIVATE_SUCCESS.format(
                                   email=app.config['EMAIL_TEMPLATE'].format(good_member)))

    assert len(outbox) == 1
    assert outbox[0].subject == Messages.ACTIVATION_SUBJECT
    assert '{{' not in outbox[0].body

    user = Member.query.get(good_member)

    assert user.quota == app.config['QUOTA']
    assert user.id == good_member
    assert user.email == app.config['EMAIL_TEMPLATE'].format(good_member)

    app.config['USE_MEMBERS_LIST'] = False

    resp = activate(client, good_memb_code, bad_member)

    assert resp == render_template("message.html",
                                   good=Messages.ACTIVATE_SUCCESS.format(
                                       email=app.config['EMAIL_TEMPLATE'].format(bad_member)))
    member = Member.query.get(bad_member)

    assert member.id == bad_member


def test_register(client, temp_ftp):
    _, host = temp_ftp
    resp = activate(client, good_memb_code, good_member)
    resp = register(client, bad_sponse_code, good_email, good_mc_user)

    assert resp == render_template("message.html", bad=Messages.WRONG_SPONSOR_CODE)

    user = Member.query.get(good_member)

    resp = register(client, user.sponsor_code, good_email, bad_mc_user)

    assert resp == render_template("message.html", bad=Messages.UNKNOWN_USERNAME)

    with mail.record_messages() as outbox:
        resp = register(client, user.sponsor_code, good_email, good_mc_user)

    assert len(outbox) == 2
    assert outbox[0].subject == Messages.REGISTRATION_SUBJECT
    assert outbox[1].subject == Messages.REGISTRATION_ALERT_SUBJECT
    assert '{{' not in outbox[0].body
    assert '{{' not in outbox[1].body

    assert resp == render_template("message.html", good=Messages.REGISTER_SUCCESS.format(email=good_email))

    w = Whitelist.query.get(good_mc_user)
    user = Member.query.get(good_member)

    assert user.quota == app.config['QUOTA'] - 1

    resp = register(client, user.sponsor_code, good_email, good_mc_user2)

    w2 = Whitelist.query.get(good_mc_user2)
    user = Member.query.get(good_member)

    assert user.quota == app.config['QUOTA'] - 2

    assert json.loads(read_file(host, app.config['FTP_WHITELIST_PATH'])) == test_mj_resp


def test_ftp(temp_ftp):
    _, host = temp_ftp

    test_text = f"Definitely did work {time.time()}"
    sub_test_text = test_text + ' SUB'
    write_file(host, "basedir/test.txt", test_text)
    assert read_file(host, "basedir/test.txt") == test_text
    assert set(host.listdir('basedir')) == {'test.txt', 'subdir'}

    sub_file = 'basedir/subdir/subtest.txt'

    write_file(get_host(), sub_file, sub_test_text)
    assert read_file(host, sub_file) == sub_test_text
    assert set(host.listdir('basedir/subdir')) == {'subtest.txt'}

    to_dir = tempfile.TemporaryDirectory()
    to_path = Path(to_dir.name)

    copy_dir(host, '', to_path)

    assert (to_path / 'basedir/test.txt').read_text() == test_text
    assert (to_path / 'basedir/subdir/subtest.txt').read_text() == sub_test_text


def test_cli(client, temp_ftp):
    _, host = temp_ftp

    database = Path(app.config['SQLALCHEMY_DATABASE_URI'])

    runner = app.test_cli_runner()

    resp = activate(client, app.config['ACCESS_CODE'], good_member)

    user = Member.query.get(good_member)

    resp = register(client, user.sponsor_code, good_email, good_mc_user)

    assert len(Member.query.all()) > 0
    assert len(Whitelist.query.all()) > 0

    runner.invoke(reset_db)

    assert len(Member.query.all()) == 0
    assert len(Whitelist.query.all()) == 0

    resp = activate(client, '', good_member)

    user = Member.query.get(good_member)

    resp = register(client, user.sponsor_code, good_email, good_mc_user)

    user = Member.query.get(good_member)

    w = Whitelist(username='TestName',
                  sponsor=user,
                  id='a62b155cde184c2ca993fa68b987901d',
                  email='Test@testemail.com')

    db.session.add(w)
    db.session.commit()

    assert json.loads(read_file(host, app.config['FTP_WHITELIST_PATH'])) != Whitelist.serialise()

    runner.invoke(force_sync)

    assert json.loads(read_file(host, app.config['FTP_WHITELIST_PATH'])) == Whitelist.serialise()

    backup_dir = tempfile.TemporaryDirectory()
    backup_dir_path = Path(backup_dir.name)

    app.config['BACKUP_DESTINATION'] = backup_dir_path

    runner.invoke(backup)

    now_ = get_now()

    for source in app.config['BACKUP_SOURCES']:
        for ((s_root, _, s_files),
            (d_root, _, d_files)) in zip(host.walk(source),
                                        os.walk(backup_dir_path / now_ / source)):
                s_root, d_root = Path(s_root), Path(d_root)

                for s_file, d_file in zip(s_files, d_files):
                    assert read_file(host, (s_root / s_file).as_posix()) == (d_root / d_file).read_text()

    runner.invoke(backup)

    backups = os.listdir(backup_dir_path)
    backups.sort(key=lambda backup: datetime.datetime.strptime(backup, app.config['BACKUP_DIR_FORMAT']))
    outdated = outdated_backups()

    assert backups == [item[1].name for item in outdated]

    runner.invoke(backup, ['--clean'])

    backups = os.listdir(backup_dir_path)
    assert all(item not in backups for item in outdated) is True
    assert len(backups) == app.config['BACKUP_ROTATION']
