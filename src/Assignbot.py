# Using discord.py for Discord API - https://discordpy.readthedocs.io/en/stable/index.html
import discord
from discord.ext import commands
# Using APSW for SQLite Database Management - https://rogerbinns.github.io/apsw/example.html
import apsw
# Using json for config stuff
import json

# Initialize Bot
#intents = discord.Intents(guilds=True, members=True, reactions=True)
client = commands.Bot(command_prefix='.')

# Load Configuration Options
configFile = open('data/config.json')
config = json.load(configFile)
configFile.close()

# Establish Connection to Database
database = apsw.Connection("data/db.sqlite")
dbCursor = database.cursor()

# Events
@client.event
async def on_ready():
    print('AssignBot Turned On...')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command()
async def shutdown(ctx):
    await ctx.send("Bot is shutting down.")
    await client.close()
    database.close(True)
    print("AssignBot Closed...")

#@client.command()
#async def setjoinrole(ctx, joinRoleID):


client.run(config['token'])
