# FireBot
This is based off of [AssignBot](https://github.com/Michael-Long/Assignbot), but expands the bot to accomplish more tasks. More of a personal bot than to be used by others, as the features added are ones that my personal server's wanted.

## Current Features
* Assign a role to new users when they join in a server
* Able to handle multiple servers with a single running instance
* Saves data to a local file to maintain information after shutdown

## Installation
Before the program can be executed, ensure you have python installed on whatever machine you intend to run it on. It has been personally tested on Python 3.8.10, but other versions might work fine too. The bot does use [Discord.py](https://discordpy.readthedocs.io/en/stable/), so whatever version of python they're requiring this will also require.

Once Python is installed, you can run the `Assignbot.py` file. This can be ran with:

```
python Assignbot.py
```

On the initial run, the bot will notify you that the `data/config.json` file was incorrectly setup. This will create the file with the fields that need to be initialized. If the file fails to generate, the default configuration would be as such:

```json
{
    "ownerID": "your-id-here",
    "token": "your-bot-token-here"
}
```

Where you'd put your personal ID into `ownerID`, and the token for your bot in `token`. Once those fields are filled, restart the bot and it should start up just fine!

## Commands

When the bot is running, it has a few commands that you can use. The prefix for all these commands is a period.

* .ping
  * Simply replies `Pong!` with how many milliseconds it took to respond.
* .shutdown
  * Safely shuts down the bot, closing any connections to open files.
  * Only the user defined within the `OwnerID` can run this command.
* .setjoinrole [id]
  * Sets the role that new users to this server will be assigned.
* .setloggingchannel
  * Redirects all bot messages to the channel this command was issued in.