from pathlib import Path
import shutil

from flask import render_template, request, Blueprint, current_app
import click

from MinerClub.database import Member, Whitelist, db

from .config import Messages
from MinerClub.membership import get_mj_id
from MinerClub.membership import is_member
from MinerClub.server_comms import update_whitelist, get_now, file_manager, outdated_backups

minerclub = Blueprint('minerclub', __name__)


@minerclub.route('/')
def home():
    return render_template('home.html', title='Home', club_name=current_app.config['CLUB_NAME'])


@minerclub.route('/activate', methods=['POST', 'GET'])
def activate():
    if request.method == 'POST':
        member_id = request.form.get('member_id')

        if request.form.get('code') != current_app.config['ACCESS_CODE']:
            code = request.form.get('code')
            current_app.logger.warn('Invalid access code provided "{}"'.format(code))
            return render_template("message.html", bad=Messages.WRONG_ACCESS_CODE)

        if current_app.config['USE_MEMBERS_LIST'] and not is_member(member_id):
            current_app.logger.warn('Invalid member ID provided "{}"'.format(member_id))
            return render_template("message.html", bad=Messages.WRONG_MEMBER_ID)

        if Member.query.get(member_id) is not None:
            current_app.logger.warn('Attempt to re-activate account "{}"'.format(member_id))
            return render_template("message.html", bad=Messages.ALREADY_ACTIVATED)

        current_app.logger.debug("Creating new member entry for {}".format(member_id))
        u = Member(id=member_id)
        db.session.add(u)

        current_app.logger.debug("Sending activation email")
        u.send_activate_email()

        current_app.logger.debug("Committing changes")
        db.session.commit()

        current_app.logger.info("Account {} successfully activated".format(member_id))
        return render_template("message.html", good=Messages.ACTIVATE_SUCCESS.format(email=u.email))

    return render_template("activate.html", title='Activate')


@minerclub.route('/register', methods=['GET', 'POST'])
def register():
    sponsor_code = request.args.get('sponsor_code', '')
    if request.method == 'POST':
        sponsor_code, username, email = (request.form.get('sponsor_code'),
                                        request.form.get('username'),
                                        request.form.get('email'))

        sponsor = Member.query.filter_by(sponsor_code=sponsor_code.strip()).first()

        if sponsor is None:
            current_app.logger.warn("Attempt to register with invalid sponsor code {}".format(sponsor_code))
            return render_template("message.html", bad=Messages.WRONG_SPONSOR_CODE)

        if sponsor.quota < 1:
            current_app.logger.warn("Attempted registration for Member {} who's quota is done".format(sponsor.id))
            return render_template("message.html", bad=Messages.OUTTA_GUESTS)

        mj_id = get_mj_id(username)

        if mj_id is None:
            current_app.logger.warn("Attempted registration for invalid MJ username {}".format(username))
            return render_template("message.html", bad=Messages.UNKNOWN_USERNAME)

        if Whitelist.query.get(username):
            current_app.logger.warn("Attempted registration for already registered username {}".format(username))
            return render_template("message.html", bad=Messages.ALREADY_WHITELISTED)

        current_app.logger.debug("Creating new whitelist entry")
        w = Whitelist(username=username, sponsor=sponsor, id=mj_id, email=email)
        db.session.add(w)

        current_app.logger.debug("Sending registration emails for {}".format(w))
        w.send_register_emails()

        current_app.logger.debug("Committing changes")
        db.session.commit()

        current_app.logger.debug("Syncing whitelists")
        update_whitelist(Whitelist)

        current_app.logger.info("Successful registration of {} sponsored by {}".format(username, sponsor.id))
        return render_template("message.html", good=Messages.REGISTER_SUCCESS.format(email=email))

    return render_template("register.html", sponsor_code=sponsor_code, title='Register')


@minerclub.route('/privacy')
def privacy():
    return render_template('privacy.html', title='Privacy Policy', club_name=current_app.config['CLUB_NAME'])


@minerclub.cli.command("init", help="Initialise application database")
def init_db():
    click.echo("Creating database")
    db.create_all()
    click.echo("Committing change")
    db.session.commit()
    click.echo("Success")


@minerclub.cli.command("reset-db", help="Wipe all database entries")
def reset_db():
    click.echo("Dropping all tables")
    db.drop_all()
    db.session.commit()
    click.echo("Recreating them")
    db.create_all()
    db.session.commit()
    click.echo("Success")


@minerclub.cli.command("force-sync", help="Force overwriting of server whitelist with MinerClub whitelist.")
def force_sync():
    click.echo("Forcing whitelist sync")
    update_whitelist(Whitelist)
    click.echo("Success")


@minerclub.cli.command('backup', help="Perform backup of server folders")
@click.option('--cycle/--no-cycle', default=True, help="Delete old backups? (defaults true)")
def backup(cycle):
    if cycle:
        click.echo("Cleaning up old backups")
        click.echo("Keeping roation of {} backups".format(current_app.config['BACKUP_ROTATION']))
        outdated = outdated_backups()
        for date, folder in outdated:
            click.echo("'{}' outdated - removing".format(folder.path, date))
            shutil.rmtree(folder.path)
            click.echo("Success")

    sources = current_app.config['BACKUP_SOURCES']
    destination = Path(current_app.config['BACKUP_DESTINATION']) / get_now()

    click.echo("Backing up {} to {}".format(sources, destination))

    click.echo("Making backup directory")
    destination.mkdir()
    click.echo("Success")
    with file_manager.get_host() as host:
        for source in sources:
            click.echo("Copying {} to {}".format(source, destination))
            file_manager.copy_dir(host, source, destination)
            click.echo("Success")

    click.echo("Complete")
