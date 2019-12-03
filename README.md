# Miner Club

Miner Club is a ready made webapp built to help people run Minecraft servers with access limited to those within the 'club'
and a limited number of guests.

From the list of registered Minecraft usernames Miner Club generates a whitelist automatically and then syncs this
whitelist with a remove server over FTP.

## Getting started

1. Clone (or download and unzip) this repo! `git clone https://github.com/0Hughman0/MinerClub`
2. Navigate into the directory with `Pipfile` in it.
3. Install the dependencies (requires pipenv!) via `pipenv install`
4. Configure your app by setting the following environment variables:

| variable name  | form                        | description                                                                                     |
|----------------|-----------------------------|-------------------------------------------------------------------------------------------------|
| SERVER_IP      | IP:HOST                     | The IP address of your Minecraft server                                                         |
| FTP_IP         | IP                          | The IP address of the FTP server (probably the same as server!)                                 |
| FTP_USER       |                             | Username to authenticate FTP with.                                                              |
| FTP_PASSWORD   |                             | Password to authenticate FTP with.                                                              |
| FTP_BASEDIR    | path/to/dir                 | Path from FTP top-level directory to where whitelist file stored.                               |
| EMAIL_TEMPLATE | {}@host                     | Template to generate email address from members list. (fills {} with member id)                 |
| MAIL_PASSWORD  |                             | Password to authenticate email sending (I recommend generating app passwords when using gmail!) |
| MAIL_USERNAME  | mail@host                   | Email address to send emails from.                                                              |
| MAIL_SERVER    | some.server.com             | Address of mail server.                                                                         |
| DISCORD_URL    | https://discord.gg/XXXXXXXX | Link sent to users for them to join Discord server.                                             |
| CLUB_NAME      | YourClub                    | Name of your club.                                                                              |
| ACCESS_CODE    | XXXXXXXXXXXXXXXXX           | Code required for users to enter to prove membership of club.                                   |
| CODE_HASH      | XXXXXXXXXXXXXXXXX           | Salt applied to member names to generate register urls. Set to something unpredictable.         |
| WHITELIST_FILE | whitelist.json              | Filename of whitelist.                                                                          |
| ADMIN_EMAIL    | admin@host.com              | Contact details of whoever maintains the website/ server.                                       |
| ADMIN_NAME     | Mr Admin                    | Name of administrator.                                                                          |

5. Navigate to the `MinerClub/data/members.csv` file and replace the examples with the 'Membership IDs' of your members
(one per line). When users activate their accounts, the name they provide must be in this file. In most cases I'd expect
this to be a list of emails (and then set `EMAIL_TEMPLATE={}`).
6. Make any changes you want to the template files, in particular the email templates and the privacy policy template.
7. Set the environment vairable `FLASK_APP=MinerClub:app`
8. Initialise the database by entering `pipenv run flask init-db`
8. Run the server using your preferred method. Note that I thoroughly recommend using https in order to ensure security.
9. Set your Minecraft server to refresh the whitelist regularly.

## Additional Helpers

The app provides the following additional commands (ran by `flask command-name`):

* `reset-db` - This completely clears the database.
* `force-sync` - This forces the app to sync the current whitelist version with the server (useful if making manual changes)

To assist with any manual changes, the app provides both the `get_shell.bat` and `get_shell.sh` scripts. Once in a shell
you can use `from st import *` to import a few helper functions/ variables.

## Notes

Don't run this server if you don't know what you're doing, you are storing peoples emails, so this needs to be done
securely.

Although I use the word 'sync', the app actually just completely overwrites the old `whitelist.json` file, so be careful
about data-loss.

Whilst the app is able to keep the `whitelist.json` file up to date, your Minecraft server instance still needs to
reload the whitelist for these changes to take effect. Most server hosts provide a tasks feature that can be used to
automatically run a `whitelist reload` command. (You might also be able to achieve this through plugins).
