
# Miner Club

Miner Club is a ready made web app built to help people run Minecraft servers with access limited to those within the 'club'  and a limited number of guests.

Users first activate their accounts, verifying their identity by providing an access code.

After this, an email is sent to them with a unique link that allows them and a defined quota of users to add their names to the whitelist.

The list of registered Minecraft usernames Miner Club generates a whitelist automatically and then syncs this whitelist with a remove server over SFTP, FTPS or FTP.

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
|  `USE_MEMBERS_LIST`  |         True/False          |               True               | Check `members.csv` for Membership ID to check for membership, or `False` to allow anyone with access code.                 |
|   `EMAIL_TEMPLATE`   |           {}@host           |                 {}               | Template to generate email address from members list. (fills {} with member id)                                             |
|     `ADMIN_NAME`     |          Admin Name         |              (blank)             | Name of administrator.                                                                                                      |
|     `ADMIN_EMAIL`    |        admin@host.com       |              (blank)             | Contact details of whoever maintains the website/ server.                                                                   |
|     `DISCORD_URL`    | https://discord.gg/XXXXXXXX |              (blank)             | Link sent to users for them to join Discord server.                                                                         |
|   `BACKUP_SOURCES`   |        dir1,dir2,dir3       | world,world_the_end,world_nether |  Comma separated list of paths to directories to backup using the backup command. (Paths relative to the top-level FTP dir) |
| `BACKUP_DESTINATION` |         path/to/dir         |              backups             |  Path to directory to store backups in. This can be relative to cwd or an absolute path.                                    |
|  `BACKUP_DIR_FORMAT` |      %y-%m-%d (%Hh%Mm)      |         %y-%m-%d_(%Hh%Mm)        | Format string filled using `datetime.strftime` to timestamp directories for a given backup.                                 |
|  `BACKUP_ROTATION`   |              1              |                 3                | Number of newest backups will preserve. Outdated backups will be deleted unless --no-cycle specified (see below).           |
|     `MAIL_SERVER`    |       some.server.com       |                 -                | Address of mail server.                                                                                                     |
|      `MAIL_PORT`     |             587             |                587               | Port to connect to on mail server.                                                                                          |
|    `MAIL_USE_TLS`    |             True            |               True               | Use TLS encryption for mail sending (depends on mail server config).                                                        |
|    `MAIL_USERNAME`   |           Username          |                 -                | Username to connect to mail server with.                                                                                    |
|    `MAIL_PASSWORD`   |           Password          |                 -                | Password to connect to mail server with. (If using Gmail I recommend setting up an app password).                           |
|    `DATABASE_FILE`   |     path/to/database.db     |            database.db           | Path to database file... not sure why you'd change this!                                                                    |

5. Next you need to configure the way MinerClub writes the updated whitelist to your server. To do this you need to set the `FILE_ENGINE` variable. How you do this depends on where you have your Minecraft Server running. Your current options are:

| Name           | Description                                                                                                                                                                                 |
|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| SFTP (default) | The secure file transfer protocol, a secure layer built upon SSH. Remotely transfer files between MinerClub and your server. Most secure and easiest to set up.                             |
| FTP            | The file transfer protocol. Widely supported, but note that authentication is done in plain text, so usernames and passwords must be disposable.                                            |
| FTPS           | FTP Secure, a modified FTP implementation that uses SSL to secure the connection (i.e. no plain text authentication). Requires some slightly involved configuration server and client side. |
| LOCAL          | If your Minecraft Server instance is running on the same machine, use this!                                                                                                                 |

5. Each `FILE_ENGINE` has its own configuration options:
  * SFTP

| Name                   | Example              | Default       | Description                                                               |
|------------------------|----------------------|---------------|---------------------------------------------------------------------------|
| `SFTP_WHITELIST_PATH`  | folder/whitelist.txt | whitelist.json | Path from SFTP top directory to the whitelist file.                       |
| `SFTP_SERVER_ADDRESS`  | 172.217.169.36       |  -            | IP address of SFTP server                                                 |
| `SFTP_SERVER_USERNAME` | username             | -             | Username to authenticate SFTP with.                                       |
| `SFTP_SERVER_PASSWORD` | password             | -             | Password to authenticate SFTP with.                                       |
| `SFTP_SERVER_PORT`     | 532                  | 22            | Port to connect to for SFTP server.                                       |
| `SFTP_HOSTKEY_CHECK`   | False/True           | True          | If `False` will not perform hostkey check when connecting to SFTP server. |
  * FTP:

| Name                  | Example              | Default       | Description                                                           |
|-----------------------|----------------------|---------------|-----------------------------------------------------------------------|
| `FTP_WHITELIST_PATH`  | folder/whitelist.txt | whitelist.json | Path from SFTP top directory to the whitelist file.                   |
| `FTP_SERVER_ADDRESS`  | 172.217.169.36       |  -            | IP address of SFTP server                                             |
| `FTP_SERVER_USERNAME` | username             | -             | Username to authenticate FTP with. (Note this is sent in plain text!) |
| `FTP_SERVER_PASSWORD` | password             | -             | Password to authenticate FTP with. (Note this is sent in plain text!) |
| `FTP_SERVER_PORT`     | 532                  | 21            | Port to connect to for FTP server.                                    |

  * FTPS (Note to use this method you need to generate a public and private keypair server-side, and install the public key onto the machine running MinerClub):

| Name                   | Example              | Default       | Description                                         |
|------------------------|----------------------|---------------|-----------------------------------------------------|
| `FTPS_WHITELIST_PATH`  | folder/whitelist.txt | whitelist.json | Path from FTPS top directory to the whitelist file. |
| `FTPS_SERVER_ADDRESS`  | 172.217.169.36       |  -            | IP address of FTPS server                           |
| `FTPS_SERVER_USERNAME` | username             | -             | Username to authenticate FTPS with.                 |
| `FTPS_SERVER_PASSWORD` | password             | -             | Password to authenticate FTPS with.                 |
| `FTPS_SERVER_PORT`     | 532                  | 21            | Port to connect to for FTPS server.                 |
  * LOCAL:

| Name                   | Example              | Default        | Description                                                   |
|------------------------|----------------------|----------------|---------------------------------------------------------------|
| `LOCAL_SERVER_DIR`     | Path/to/server/      | -              | Path to the folder containing your Minecraft Server instance. |
| `LOCAL_WHITELIST_PATH` | folder/whitelist.txt | whitelist.json | Path from `LOCAL_SERVER_DIR` to the whitelist.json file.      |


5. Navigate to the `members.csv` file and replace the examples with the 'Membership IDs' of your members  (one per line), or set `USE_MEMBERS_LIST=False` in your config to allow anyone with the access code to join. If `True`,
when users activate their accounts, the name they provide must be in this file. In most cases I'd expect this to be a
list of emails (meaning that `EMAIL_TEMPLATE={}`).
6. Make any changes you want to the template files, in particular the email templates and the privacy policy template.
Note that because these are rendered by the flask application, you can access the `app.config` object and the `member` or `whitelist` object.
7. Set the environment variable `FLASK_APP=app`
8. Initialise the database by entering `pipenv run flask minerclub init`
8. Run the server using your preferred method. Note that I thoroughly recommend using https in order to ensure security.
9. Set your Minecraft server to refresh the whitelist regularly.

## Customisation

This is a Flask app and hence makes use of Jinja2 templating. You are welcome (and encouraged) to make your own changes
to the `.html` and `.txt` templates found in the `MinerClub/templates` directory.

## Additional Helpers

The app provides the following additional commands (ran with `pipenv run flask minerclub command-name`):

* `reset-db` - This completely clears the database.
* `force-sync` - This forces the app to sync the current whitelist version with the server (useful if making manual changes)
* `backup --cycle` or `backup --no-cycle` - This creates a local copy of server directories from your config (defaults to
'world', 'world_nether' and 'world_the_end').

For slightly more info, run `pipenv run flask minerclub --help`.

To assist with any manual changes, the app provides both the (get shell) `gs.bat` and `gs.sh` scripts. Once in a shell
you can use (shell tools) `from st import *` to import a few helper functions/ variables.

## Notes

Don't run this server if you don't know what you're doing, you are storing peoples emails, so this needs to be done
securely.

Although I use the word 'sync', the app actually just completely overwrites the old `whitelist.json` file, so be careful
about data-loss.

Whilst the app is able to keep the `whitelist.json` file up to date, your Minecraft server instance still needs to
reload the whitelist for these changes to take effect. Most server hosts provide a tasks feature that can be used to
automatically run a `whitelist reload` command. (You might also be able to achieve this through plugins).

Once everything is set up you can run the set of integration tests using `pipenv run pytest` to check everything is
working fine (they take a little while!).

## More Notes

If you are having trouble with installation of dependencies like bcrypt and cryptography, make sure you are using the
latest version of pip (this caused me an immense deal of frustration recently!)