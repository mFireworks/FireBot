# FireBot
This is based off of [AssignBot](https://github.com/Michael-Long/Assignbot), but expands the bot to accomplish more tasks. More of a personal bot than to be used by others, as the features added are ones that my personal server's wanted.

## Current Features
* Assign a role to new users when they join in a server
* Able to handle multiple servers with a single running instance
* Saves data to a local file to maintain information after shutdown
* Can create "Bingo Board" codes based upon my [Viewer Bingo](https://github.com/Michael-Long/Viewer-Bingo) project when requested by a user.

## Installation
Before the program can be executed, ensure you have python installed on whatever machine you intend to run it on. It has been personally tested on Python 3.8.10, but other versions might work fine too. The bot does use [Discord.py](https://discordpy.readthedocs.io/en/stable/), so whatever version of python they're requiring this will also require.

Once Python is installed, you can run the `Assignbot.py` file. This can be ran with:

```
python3 Assignbot.py
```

On the initial run, the bot will notify you that the `data/config.json` file was incorrectly setup. This will create the file with the fields that need to be initialized. If the file fails to generate, the default configuration would be as such:

```json
{
    "token": "your-bot-token-here",
    "enableConsoleLogging": true
}
```

`token`: This represent the token ID for your Discord Application. This can be setup from the [Discord Developer Portal](https://discord.com/developers/applications). More information on setting up a Discord Bot can be found [Here](https://www.youtube.com/watch?v=xc1VpbRd4is). During the setup of this bot, you'll have to enable the following Bot Permissions at minimum (or you can just give it Administrative Permissions):
* Server Members Intent
* View Channels
* Manage Roles
* Send Messages
* Add Reactions
* Use External Emoji
* Manage Messages
* Read Message History

`enableConsoleLogging`: This indicates whether or not the bot should print logging information to the console it's running from. Having this on is recommended, but disabling it will keep the console clean.

Once you've entered your Bot Token ID, you should be able to run the program again and it should be up and running! Once it's running, you'll then have to generate invite links from the bot's page on the [Discord Developer Portal](https://discord.com/developers/applications) to add it to servers.

## Setting Admin Roles

Once you have the bot running and have added it to some servers, it's ideal to set some roles within the server as `Admin` roles for the bot. When no roles are defined, it'll default to user's with the `Manage Server` permission. You can add and remove Admin roles with the following commands:

* .addAdminRole [roleId]
  * Adds the specified role as an Admin role for the bot on this server.
* .removeAdminRole [roleId]
  * Removes the specified role as an Admin role for the bot on this server.
* .listAdminRoles
  * Lists all the roles stored as an Admin role on this server. Will say "No Roles Found" when none are present.

## Commands

When the bot is running, it has a few commands that you can use. The prefix for all these commands is a period.

* .ping
  * Simply replies `Pong!` with how many milliseconds it took to respond.
  * Permissions: All Users
* .shutdown
  * Safely shuts down the bot, closing any connections to open files.
  * Permissions: All Admin Users
* .setJoinRole [roleId]
  * Sets the role that new users to this server will be assigned.
  * Permissions: All Admin Users
* .setLoggingChannel
  * Redirects all Event Logging messages to this channel.
  * Permissions: All Admin Users
* .toggleBingo
  * Enables the .bingo command on this server
  * Permissions: All Admin Users
* .resetUserBingo [userID]
  * Resets the bingo board for the specified user, allowing them to generate a new bingo board.
  * Permissions: All Admin Users
* .bingo
  * When enabled, will either generate a new bingo board code for the user, or give them their saved board.
  * Permissions: All Users