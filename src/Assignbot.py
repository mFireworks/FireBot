# Using discord.py for Discord API - https://discordpy.readthedocs.io/en/stable/index.html
import discord
from discord.ext import commands
# Using APSW for SQLite Database Management - https://rogerbinns.github.io/apsw/example.html
import apsw
# Using json for config stuff
import json

# Initialize Bot
intents = discord.Intents(guilds=True, members=True, messages=True, reactions=True)
bot = commands.Bot(command_prefix='.', intents=intents)

# Load Configuration Options
configFile = open('data/config.json')
config = json.load(configFile)
configFile.close()

# Establish Connection to Database
database = apsw.Connection("data/db.sqlite")
dbCursor = database.cursor()

# Helper Functions
async def logMessage(guild, defaultChannel, message):
    loggingID = list(dbCursor.execute("select LoggingChannelID from main where ServerID = ?", (guild.id, )))
    if (len(loggingID) == 0):
        if (defaultChannel == None):
            print(message)
        else:
            await defaultChannel.send(message)
        return
    logChannel = guild.get_channel(int(loggingID[0][0]))
    if (logChannel == None):
        if (defaultChannel == None):
            print(message)
        else:
            await defaultChannel.send(message)
        return
    await logChannel.send(message)

# Events
@bot.event
async def on_ready():
    print('AssignBot Turned On...')

@bot.event
async def on_member_join(member):
    print("We have triggered the join event")
    joinRoleID = list(dbCursor.execute("select JoinRoleID from main where ServerID = ?", (member.guild.id, )))
    if (len(joinRoleID) == 0):
        await logMessage(member.guild, None, member.guild.name + " doesn't have a join role set")
        return

    role = discord.utils.get(member.guild.roles, id=int(joinRoleID[0][0]))
    await member.add_roles(role)
    await logMessage(member.guild, None, "Sent " + member.name + " to auto-join role " + role.name)

# Commands
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def shutdown(ctx):
    if (ctx.author.id != int(config['ownerID'])):
        return
    await logMessage(ctx.guild, ctx.channel, "Bot is shutting down.")
    await bot.close()
    database.close(True)
    print("AssignBot Closed...")

@bot.command()
async def setjoinrole(ctx, joinRoleID):
    joinRole = ctx.guild.get_role(int(joinRoleID))
    if (joinRole == None):
        await logMessage(ctx.guild, ctx.channel, "Provided role not found.")
        return

    serverEntries = list(dbCursor.execute("select ServerID from main where ServerID = ?", (ctx.guild.id, )))
    if (len(serverEntries) == 0):
        dbCursor.execute("insert into main (ServerID, JoinRoleID) values (?, ?)", (ctx.guild.id, joinRoleID))
    else:
        dbCursor.execute("update main set JoinRoleID = ? where ServerID = ?", (joinRoleID, ctx.guild.id))
    await logMessage(ctx.guild, ctx.channel, joinRole.name + " has been set as the auto-join role for " + ctx.guild.name)

@bot.command()
async def setloggingchannel(ctx):
    serverEntry = list(dbCursor.execute("select ServerID from main where ServerID = ?", (ctx.guild.id, )))
    if (len(serverEntry) == 0):
        dbCursor.execute("insert into main (ServerID, LoggingChannelID) values (?, ?)", (ctx.guild.id, ctx.channel.id))
    else:
        dbCursor.execute("update main set LoggingChannelID = ? where ServerID = ?", (ctx.channel.id, ctx.guild.id))
    await logMessage(ctx.guild, ctx.channel, "#" + ctx.channel.name + " set as the logging channel for AssignBot.")

bot.run(config['token'])
