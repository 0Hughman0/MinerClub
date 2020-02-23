import time
import json
from pathlib import Path
import os
import datetime

import pytest

from flask import render_template

from MinerClub import mail, create_app
from MinerClub.database import db
from MinerClub.config import Debug, Messages
from MinerClub.site import reset_db, force_sync, backup
from MinerClub.database import Member, Whitelist
from MinerClub.membership import is_member
from MinerClub.server_comms import file_manager, get_now, outdated_backups

from .helpers import TestFTPServer, TestSFTPServer

app = create_app('debug')

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
def server_filesystem(tmp_path):
    base_dir = tmp_path / 'basedir'
    base_dir.mkdir()
    sub_dir = base_dir / 'subdir'
    sub_dir.mkdir()
    yield tmp_path


@pytest.fixture(params=file_manager.engines.keys())
def with_engine(server_filesystem, monkeypatch, request):
    server_home = server_filesystem
    engine = request.param
    monkeypatch.setitem(app.config, 'FILE_ENGINE', engine)

    with app.app_context():
        if engine in ('FTP', 'FTPS'):
            server = TestFTPServer(file_manager.username,
                                   file_manager.password,
                                   file_manager.address,
                                   file_manager.port,
                                   file_manager.engine_name == 'FTPS',
                                   server_home.as_posix())
        elif engine == 'SFTP':
            server = TestSFTPServer(file_manager.username,
                                   file_manager.password,
                                   file_manager.address,
                                   file_manager.port, server_home.as_posix())
        else:
            monkeypatch.setitem(app.config, 'LOCAL_SERVER_DIR', server_home)
            server = None

        if not server:
            yield server_home
        else:
            with server:
                yield server_home


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


def test_register(client, with_engine, server_filesystem):

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

    with file_manager.get_host() as host:
        assert json.loads(file_manager.read_text(host, file_manager.whitelist)) == test_mj_resp


def test_engines(with_engine, server_filesystem, tmp_path_factory):

    host = file_manager.get_host()

    test_text = f"Definitely did work {time.time()}"
    sub_test_text = test_text + ' SUB'
    file_manager.write_text(host, "basedir/test.txt", test_text)
    assert file_manager.read_text(host, "basedir/test.txt") == test_text
    assert set(file_manager.listdir(host, 'basedir')) == {'test.txt', 'subdir'}

    sub_file = 'basedir/subdir/subtest.txt'

    file_manager.write_text(file_manager.get_host(), sub_file, sub_test_text)
    assert file_manager.read_text(host, sub_file) == sub_test_text
    assert set(file_manager.listdir(host, 'basedir/subdir')) == {'subtest.txt'}

    tmp_path = tmp_path_factory.mktemp('backup')

    file_manager.copy_dir(host, 'basedir', tmp_path)

    assert (tmp_path / 'basedir/test.txt').read_text() == test_text
    assert (tmp_path / 'basedir/subdir/subtest.txt').read_text() == sub_test_text


def test_cli(client, monkeypatch, with_engine, tmp_path, server_filesystem):

    database = Path(app.config['SQLALCHEMY_DATABASE_URI'])

    runner = app.test_cli_runner()

    resp = activate(client, app.config['ACCESS_CODE'], good_member)

    user = Member.query.get(good_member)

    resp = register(client, user.sponsor_code, good_email, good_mc_user)

    assert len(Member.query.all()) > 0
    assert len(Whitelist.query.all()) > 0

    assert runner.invoke(reset_db).exception is None

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

    with file_manager.get_host() as host:
        assert json.loads(file_manager.read_text(host, file_manager.whitelist)) != Whitelist.serialise()

    assert runner.invoke(force_sync).exception is None

    with file_manager.get_host() as host:
        assert json.loads(file_manager.read_text(host, file_manager.whitelist)) == Whitelist.serialise()

    backups_dir = tmp_path / 'backups'
    backups_dir.mkdir()
    monkeypatch.setitem(app.config, 'BACKUP_DESTINATION', backups_dir)

    now_ = get_now()

    assert runner.invoke(backup).exception is None

    first_backup = backups_dir / now_

    with file_manager.get_host() as host:
        for source in app.config['BACKUP_SOURCES']:
            source_files = list(file_manager.walk(host, source))
            destination_files = list(os.walk(first_backup / source))

            assert len(source_files) == len(destination_files)

            for ((s_root, _, s_files), (d_root, _, d_files)) in zip(source_files, destination_files):
                    s_root, d_root = Path(s_root), Path(d_root)

                    for s_file, d_file in zip(s_files, d_files):
                        assert file_manager.read_text(host, (s_root / s_file).as_posix()) == (d_root / d_file).read_text()

    monkeypatch.setitem(app.config, 'BACKUP_DIR_FORMAT', '%y-%m-%d (%Hh%Mm%Ss%fms)')

    first_backup.rename(first_backup.with_name(get_now()))

    assert runner.invoke(backup).exception is None

    backups = os.listdir(backups_dir)
    backups.sort(key=lambda backup: datetime.datetime.strptime(backup, app.config['BACKUP_DIR_FORMAT']))
    outdated = outdated_backups()

    assert backups == [item[1].name for item in outdated]

    assert runner.invoke(backup, ['--cycle']).exception is None

    backups = os.listdir(backups_dir)
    assert all(item not in backups for item in outdated) is True
    assert len(backups) == app.config['BACKUP_ROTATION']
