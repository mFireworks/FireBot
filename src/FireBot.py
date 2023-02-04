# Using discord.py for Discord API - https://discordpy.readthedocs.io/en/stable/index.html
import discord
from discord.ext import commands
# Using APSW for SQLite Database Management - https://rogerbinns.github.io/apsw/example.html
import apsw
# Using json for config stuff
import json
# Using Requests to query website for bingo board row count
import requests
# Using Random to generate random bingo codes
import random
# Using os for creating the config.json when it doesn't exist
import os

# Initialize Bot
intents = discord.Intents(guilds=True, members=True, messages=True, message_content=True, reactions=True)
bot = commands.Bot(command_prefix='.', intents=intents)

# Load Configuration Options
configFile = 1
configPath = 'data/config.json'
config = {}
try:
    configFile = open(configPath)
except:
    print("config.json couldn't be read! Creating the default template...")
    print("Be sure to insert your IDs into the file into the correct locations.")
    config = {
        "token": "insert-bot-token-here",
        "enableConsoleLogging": True
    }
    os.makedirs(os.path.dirname(configPath), exist_ok=True)
    with open(configPath, "w") as configFile:
        json.dump(config, configFile, indent=4)
    input("Press Enter to continue...")
    exit()
try:
    config = json.load(configFile)
except:
    print("There seems to be an issue with the config.json file. Couldn't be read as json.")
    print("Ensure the file is valid json. Deleting the file and running the program again will regenerate it.")
    input("Press Enter to continue...")
    exit()
configFile.close()

try:
    config['token']
    config['enableConsoleLogging']
except KeyError as e:
    print("Unable to find key " + str(e) + " within the config.json. Ensure it's within the file and has a valid value.")
    input("Press Enter to continue...")
    exit()

# Query Bingo Database for Count
countPayload = {'count': True}
countRequest = requests.get('https://michaeldoescoding.net/projects/pokemon/nuzlockebingo/index.php', params=countPayload)
count = 0
if (countRequest.status_code != 200):
    print("Couldn't retrieve count information, setting count to 0")
else:
    count = int(countRequest.text)

# Establish Connection to Database
database = apsw.Connection("data/db.sqlite")
dbCursor = database.cursor()
if (len(list(dbCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bingo';"))) == 0):
    dbCursor.execute("CREATE TABLE 'bingo' ('ServerID' TEXT, 'UserID' TEXT, 'BingoCode' TEXT);")
if (len(list(dbCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='adminRoles';"))) == 0):
    dbCursor.execute("CREATE TABLE 'adminRoles' ('ServerID' TEXT, 'AdminRoleID' TEXT);")
if (len(list(dbCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='flags';"))) == 0):
    dbCursor.execute("CREATE TABLE 'flags' ('ServerID' TEXT, 'JoinRoleID' TEXT, 'LoggingChannelID' TEXT, 'AllowBingo' INTEGER NOT NULL);")

# Helper Functions
async def logEvent(guild, defaultChannel, message):
    loggingID = list(dbCursor.execute("select LoggingChannelID from flags where ServerID = ?;", (guild.id, )))
    if (config['enableConsoleLogging']):
        print("Event Log Message: " + message)
    if (len(loggingID) == 0 or loggingID[0][0] == None):
        if (defaultChannel != None):
            await defaultChannel.send(message)
        return
    logChannel = guild.get_channel(int(loggingID[0][0]))
    if (logChannel == None):
        if (defaultChannel != None):
            await defaultChannel.send(message)
        return
    await logChannel.send(message)

async def logCommand(ctx, message):
    if (config['enableConsoleLogging']):
        print("Server - Channel - User: " + ctx.guild.name + " - " + ctx.channel.name + " - " + ctx.author.name + " | Executed: " + ctx.message.content + " | Response: " + message)
    await ctx.channel.send(message)

async def canUseAdminCommand(guild, channel, user):
    adminRoles = list(dbCursor.execute("select AdminRoleID from adminRoles where ServerID = ?;", (guild.id, )))
    isAdmin = False
    if (len(adminRoles) != 0):
        for role in user.roles:
            for adminRole in adminRoles:
                if (str(adminRole[0]) == str(role.id)):
                    isAdmin = True
    if (not isAdmin):
        # If they don't have any of the Admin roles or there's no admin roles, we'll see if they have the manage_guild permission or are an administrator
        isAdmin = channel.permissions_for(user).manage_guild or channel.permissions_for(user).administrator

    return isAdmin

# Events
@bot.event
async def on_ready():
    print('AssignBot Connected!')

@bot.event
async def on_member_join(member):
    joinRoleID = list(dbCursor.execute("select JoinRoleID from flags where ServerID = ?;", (member.guild.id, )))
    if (len(joinRoleID) == 0):
        await logEvent(member.guild, None, member.guild.name + " doesn't have a join role set")
        return

    role = discord.utils.get(member.guild.roles, id=int(joinRoleID[0][0]))
    await member.add_roles(role)
    await logEvent(member.guild, None, "Sent " + member.name + " to auto-join role " + role.name)

# Commands
@bot.command()
async def ping(ctx):
    await logCommand(ctx, f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def shutdown(ctx):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        await logCommand(ctx, "You need admin permissions to run this command")
        return

    await logEvent(ctx.guild, ctx.channel, "Bot is shutting down.")
    await bot.close()
    database.close(True)
    print("AssignBot Closed...")

@bot.command()
async def setJoinRole(ctx, joinRoleID):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        await logCommand(ctx, "You need admin permissions to run this command")
        return

    try:
        int(joinRoleID)
    except:
       await logCommand(ctx, "The given joinRoleID isn't an int value: " + joinRoleID)
       return

    joinRole = ctx.guild.get_role(int(joinRoleID))
    if (joinRole == None):
        await logCommand(ctx, "Provided role not found.")
        return

    serverEntries = list(dbCursor.execute("select ServerID from flags where ServerID = ?;", (ctx.guild.id, )))
    if (len(serverEntries) == 0):
        dbCursor.execute("insert into flags (ServerID, JoinRoleID, LoggingChannelID, AllowBingo) values (?, ?, ?, ?);", (ctx.guild.id, joinRoleID, ctx.channel.id, 0))
    else:
        dbCursor.execute("update flags set JoinRoleID = ? where ServerID = ?;", (joinRoleID, ctx.guild.id))
    await logCommand(ctx, joinRole.name + " has been set as the auto-join role for " + ctx.guild.name)

@bot.command()
async def addAdminRole(ctx, adminRoleID):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        await logCommand(ctx, "You need admin permissions to run this command")
        return

    try:
        int(adminRoleID)
    except:
       await logCommand(ctx, "The given adminRoleID isn't an int value: " + adminRoleID)
       return

    adminRole = ctx.guild.get_role(int(adminRoleID))
    if (adminRole == None):
        await logCommand(ctx, "Provided role not found.")
        return

    existingRoles = list(dbCursor.execute("select AdminRoleID from adminRoles where ServerID = ? and AdminRoleID = ?;", (ctx.guild.id, adminRoleID)))
    if (len(existingRoles) == 0):
        dbCursor.execute("insert into adminRoles (ServerID, AdminRoleID) values (?, ?);", (ctx.guild.id, adminRoleID))
        await logCommand(ctx, "Added " + adminRole.name + " as an admin role.")
    else:
        await logCommand(ctx, adminRole.name + " as already an admin role.")

@bot.command()
async def removeAdminRole(ctx, adminRoleID):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        await logCommand(ctx, "You need admin permissions to run this command")
        return

    try:
        int(adminRoleID)
    except:
       await logCommand(ctx, "The given adminRoleID isn't an int value: " + adminRoleID)
       return

    adminRole = ctx.guild.get_role(int(adminRoleID))
    if (adminRole == None):
        await logCommand(ctx, "Provided role not found.")
        return

    existingRoles = list(dbCursor.execute("select AdminRoleID from adminRoles where ServerID = ? and AdminRoleID = ?;", (ctx.guild.id, adminRoleID)))
    if (len(existingRoles) > 0):
        dbCursor.execute("delete from adminRoles where ServerID = ? and AdminRoleID = ?;", (ctx.guild.id, adminRoleID))
        await logCommand(ctx, "Removed " + adminRole.name + " as an admin role.")
    else:
        await logCommand(ctx, adminRole.name + " isn't an admin role.")

@bot.command()
async def listAdminRoles(ctx):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        await logCommand(ctx, "You need admin permissions to run this command")
        return

    adminRoles = list(dbCursor.execute("select AdminRoleID from adminRoles where ServerID = ?;", (ctx.guild.id,)))
    roleNames = ""
    for roleID in adminRoles:
        if (roleNames == ""):
            roleNames = ctx.guild.get_role(int(roleID[0])).name
        else:
            roleNames = roleNames + ", " + ctx.guild.get_role(int(roleID[0])).name
    if (roleNames == ""):
        roleNames = "No Roles Found"
    await logCommand(ctx, "Admin Roles: " + roleNames)

@bot.command()
async def setLoggingChannel(ctx):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        await logCommand(ctx, "You need admin permissions to run this command")
        return

    serverEntry = list(dbCursor.execute("select ServerID from flags where ServerID = ?;", (ctx.guild.id, )))
    if (len(serverEntry) == 0):
        dbCursor.execute("insert into flags (ServerID, LoggingChannelID, AllowBingo) values (?, ?, ?);", (ctx.guild.id, ctx.channel.id, 0))
    else:
        dbCursor.execute("update flags set LoggingChannelID = ? where ServerID = ?;", (ctx.channel.id, ctx.guild.id))
    await logCommand(ctx, "#" + ctx.channel.name + " set as the logging channel for AssignBot.")

@bot.command()
async def toggleBingo(ctx):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        await logCommand(ctx, "You need admin permissions to run this command")
        return

    allowBingo = list(dbCursor.execute("select AllowBingo from flags where ServerID = ?;", (ctx.guild.id, )))
    if (len(allowBingo) == 0):
        dbCursor.execute("insert into flags (ServerID, AllowBingo) values (?, ?;)", (ctx.guild.id, 1))
        await logCommand(ctx, "Bingo has been activated for this server!")
    elif (allowBingo[0][0] == 0):
        dbCursor.execute("update flags set AllowBingo = ? where ServerID = ?;", (1, ctx.guild.id))
        await logCommand(ctx, "Bingo has been activated for this server!")
    elif (allowBingo[0][0] != 0):
        dbCursor.execute("update flags set AllowBingo = ? where ServerID = ?;", (0, ctx.guild.id))
        await logCommand(ctx, "Bingo has been deactivated for this server.")

@bot.command()
async def resetUserBingo(ctx, userID):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        await logCommand(ctx, "You need admin permissions to run this command")
        return

    try:
        int(userID)
    except:
       await logCommand(ctx, "The given userID isn't an int value: " + userID)
       return

    user = ctx.guild.get_member(int(userID))
    if (user == None):
        await logCommand(ctx, "No user found in this server with ID: " + userID)
        return
    
    dbCursor.execute("delete from bingo where ServerID = ? and UserID = ?;", (ctx.guild.id, userID))
    await logCommand(ctx, "Bingo Code has been cleared from " + user.name)

@bot.command()
async def bingo(ctx):
    allowBingo = list(dbCursor.execute("select AllowBingo from flags where ServerID = ?;", (ctx.guild.id, )))
    if (len(allowBingo) > 0 and allowBingo[0][0] != 0):
        userEntry = list(dbCursor.execute("select BingoCode from bingo where ServerID = ? and UserID = ?;", (ctx.guild.id, ctx.author.id)))
        bingoCode = ""
        if (len(userEntry) == 0):
            # generate new code and put it into the table
            pickedEntries = list()
            for index in range(24):
                randEntry = random.randint(0, count - 1)
                while pickedEntries.count(randEntry) > 0:
                    randEntry = random.randint(0, count - 1)
                randEntryHex = hex(randEntry)[2:]
                while len(randEntryHex) < 4:
                    randEntryHex = "0" + randEntryHex
                bingoCode = bingoCode + randEntryHex
                pickedEntries.append(randEntry)
            dbCursor.execute("insert into bingo (ServerID, UserID, BingoCode) values (?, ?, ?);", (ctx.guild.id, ctx.author.id, bingoCode))
        else:
            bingoCode = userEntry[0][0]
        await logCommand(ctx, ctx.author.mention + " Bingo Code: " + bingoCode + "\nYou can view your bingo board here: https://michaeldoescoding.net/projects/pokemon/nuzlockebingo/index.html")

try:
    bot.run(config['token'])
except BaseException as e:
    print("An error occurred when trying to start the bot. Most likely the token given within config.json is incorrect.")
    print("Error: " + str(e))
    print()
    input("Press Enter to Exit...")
