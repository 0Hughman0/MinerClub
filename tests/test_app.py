import time
import json
import shutil
from pathlib import Path
import os

import pytest
from flask import render_template

from MinerClub import app, db, mail
from MinerClub.config import Debug, Messages, Product
from MinerClub.site import Member, Whitelist, init_db, reset_db, force_sync

from MinerClub.membership import is_member
from MinerClub.mccontrol import write_file, read_file


app.config.from_object(Debug)
db.init_app(app)
mail.init_app(app)

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
    db.drop_all()
    db.create_all()
    db.session.commit()

    with app.test_client() as client:
        yield client


class ConfigSetter:

    def __init__(self, name):
        configs = {'Debug': Debug,
                   'Product': Product}
        self.temp_conf = configs[name]

    def set_config(self, config):
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)
        db.init_app(app)
        mail.init_app(app)

    def __enter__(self):
        self.old_config = app.config.copy()
        self.set_config(self.temp_conf)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.set_config(self.old_config)


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

    user = Member.query.get(good_member)

    assert user.quota == app.config['QUOTA']
    assert user.id == good_member
    assert user.email == app.config['EMAIL_TEMPLATE'].format(good_member)


def test_register(client):
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

    assert resp == render_template("message.html", good=Messages.REGISTER_SUCCESS.format(email=good_email))

    w = Whitelist.query.get(good_mc_user)
    user = Member.query.get(good_member)

    assert user.quota == app.config['QUOTA'] - 1

    resp = register(client, user.sponsor_code, good_email, good_mc_user2)

    w2 = Whitelist.query.get(good_mc_user2)
    user = Member.query.get(good_member)

    assert user.quota == app.config['QUOTA'] - 2

    assert json.loads(read_file(app.config['WHITELIST_FILE'])) == test_mj_resp


def test_ftp():
    test_text = f"Definitely did work {time.time()}"

    with app.app_context():
        write_file("test.txt", test_text)

    with app.app_context():
        back = read_file("test.txt")

    assert back == test_text


def test_database_cli(client):
    with ConfigSetter('Product'):
        database = Path('MinerClub/database.db')
        hiddenplace = Path('tests/database.db')
        moved = False
        if database.exists():
            shutil.move(database, hiddenplace)
            moved = True

        assert database.exists() is False

        runner = app.test_cli_runner()

        runner.invoke(init_db)

        assert database.exists() is True

        resp = activate(client, app.config['ACCESS_CODE'], good_member)

        user = Member.query.get(good_member)

        resp = register(client, user.sponsor_code, good_email, good_mc_user)

        assert len(Member.query.all()) > 0
        assert len(Whitelist.query.all()) > 0

        runner.invoke(reset_db)

        assert len(Member.query.all()) == 0
        assert len(Whitelist.query.all()) == 0

        db.session.close()
        os.remove(database.as_posix())

        assert database.exists() is False

        if moved:
            shutil.move(hiddenplace, database)


def test_other_cli(client):
    runner = app.test_cli_runner()

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

    assert json.loads(read_file(app.config['WHITELIST_FILE'])) != Whitelist.serialise()

    runner.invoke(force_sync)

    assert json.loads(read_file(app.config['WHITELIST_FILE'])) == Whitelist.serialise()
