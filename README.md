# Miner Club

Miner Club is a ready made web app built to help people run Minecraft servers with access limited to those within the 'club'
and a limited number of guests.

Users first activate their accounts, verifying their identity by providing an access code.

After this, an email is sent to them with a unique link that allows them and a defined quota of users to add their names to the whitelist.

The list of registered Minecraft usernames Miner Club generates a whitelist automatically and then syncs this
whitelist with a remove server over FTP.

## Getting started

1. Clone (or download and unzip) this repo! `git clone https://github.com/0Hughman0/MinerClub`
2. Navigate into the directory with `Pipfile` in it.
3. Install the dependencies (requires pipenv!) via `pipenv install`
4. MinerClub now uses [`.env`](https://github.com/theskumar/python-dotenv) for configuration. To configure, make a file named `.env` in that directory, putting `PARAMETER=value` on each line.
4. Configure your app by setting the following environment variables:

| Name                 | Example                     | Default                          |  Description                                                                                                                |
|----------------------|-----------------------------|----------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
|      `CLUB_NAME`     |           YourClub          |                 -                | Name of your club.                                                                                                          |
|      `SERVER_IP`     |           IP:HOST           |                 -                | The IP address of your Minecraft server                                                                                     |
|     `ACCESS_CODE`    |      XXXXXXXXXXXXXXXXX      |                 -                | Code required for users to enter to prove membership of club.                                                               |
|        `QUOTA`       |              4              |                 4                |  The number of whitelist entries each member is allowed (including the member)                                              |
|      `CODE_SALT`     |      XXXXXXXXXXXXXXXXX      |                 -                | Salt applied to member names to generate register urls. Set to something unpredictable.                                     |
|   `EMAIL_TEMPLATE`   |           {}@host           |                 {}               | Template to generate email address from members list. (fills {} with member id)                                             |
|     `ADMIN_NAME`     |          Admin Name         |              (blank)             | Name of administrator.                                                                                                      |
|     `ADMIN_EMAIL`    |        admin@host.com       |              (blank)             | Contact details of whoever maintains the website/ server.                                                                   |
|     `DISCORD_URL`    | https://discord.gg/XXXXXXXX |              (blank)             | Link sent to users for them to join Discord server.                                                                         |
|       `FTP_IP`       |              IP             |                 -                | The IP address of the FTP server (probably the same as server!)                                                             |
|      `FTP_PORT`      |              21             |                21                | FTP port to connect to.                                                                                                     |
|    `FTP_USERNAME`    |             User            |                 -                | Username to authenticate FTP with.                                                                                          |
|    `FTP_PASSWORD`    |           Password          |                 -                | Password to authenticate FTP with.                                                                                          |
| `FTP_WHITELIST_PATH` |    path/to/whitelist.txt    |          whitelist.json          | Path from FTP top directory to the whitelist file.                                                                          |
|     `FTP_USE_TLS`    |             True            |               False              |  Use TLS encrypted FTP - supported in some cases.                                                                           |
|   `BACKUP_SOURCES`   |        dir1,dir2,dir3       | world,world_the_end,world_nether |  Comma separated list of paths to directories to backup using the backup command. (Paths relative to the top-level FTP dir) |
| `BACKUP_DESTINATION` |         path/to/dir         |              backups             |  Path to directory to store backups in. This can be relative to cwd or an absolute path.                                    |
|  `BACKUP_DIR_FORMAT` |      %y-%m-%d (%Hh%Mm)      |         %y-%m-%d (%Hh%Mm)        | Format string filled using `datetime.strftime` to timestamp directories for a given backup.                                 |
|     `MAIL_SERVER`    |       some.server.com       |                 -                | Address of mail server.                                                                                                     |
|      `MAIL_PORT`     |             587             |                587               | Port to connect to on mail server.                                                                                          |
|    `MAIL_USE_TLS`    |             True            |               True               | Use TLS encryption for mail sending (depends on mail server config).                                                        |
|    `MAIL_USERNAME`   |           Username          |                 -                | Username to connect to mail server with.                                                                                    |
|    `MAIL_PASSWORD`   |           Password          |                 -                | Password to connect to mail server with. (If using Gmail I recommend setting up an app password).                           |
|    `DATABASE_FILE`   |     path/to/database.db     |            database.db           | Path to database file... not sure why you'd change this!                                                                    |

5. Navigate to the `MinerClub/data/members.csv` file and replace the examples with the 'Membership IDs' of your members
(one per line). When users activate their accounts, the name they provide must be in this file. In most cases I'd expect
this to be a list of emails (meaning that `EMAIL_TEMPLATE={}`).
6. Make any changes you want to the template files, in particular the email templates and the privacy policy template.
Note that because these are rendered by the flask application, you can access the app config object.
7. Set the environment vairable `FLASK_APP=MinerClub:app`
8. Initialise the database by entering `pipenv run flask init`
8. Run the server using your preferred method. Note that I thoroughly recommend using https in order to ensure security.
9. Set your Minecraft server to refresh the whitelist regularly.

## Additional Helpers

The app provides the following additional commands (ran by `pipenv run flask command-name`):

* `reset-db` - This completely clears the database.
* `force-sync` - This forces the app to sync the current whitelist version with the server (useful if making manual changes)

To assist with any manual changes, the app provides both the (get shell) `gs.bat` and `gs.sh` scripts. Once in a shell
you can use (shell tools) `from st import *` to import a few helper functions/ variables.

The app also includes a backup tool that can fetch copies of remote directories on the FTP server and store a local copy with
a timestamp. This is done with the command `flask backup` and will behave according to your configuration. You might want
to use something like cron to schedule regular running of this command.

## Notes

Don't run this server if you don't know what you're doing, you are storing peoples emails, so this needs to be done
securely.

Although I use the word 'sync', the app actually just completely overwrites the old `whitelist.json` file, so be careful
about data-loss.

Whilst the app is able to keep the `whitelist.json` file up to date, your Minecraft server instance still needs to
reload the whitelist for these changes to take effect. Most server hosts provide a tasks feature that can be used to
automatically run a `whitelist reload` command. (You might also be able to achieve this through plugins).

Once everything is set up you can run the set of integration tests using `pipenv run pytest` to check everything is
working fine.
