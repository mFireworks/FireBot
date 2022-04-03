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

# Initialize Bot
intents = discord.Intents(guilds=True, members=True, messages=True, reactions=True)
bot = commands.Bot(command_prefix='.', intents=intents)

# Load Configuration Options
configFile = 1
config = {}
try:
    configFile = open('data/config.json')
except:
    print("config.json couldn't be read! Creating the default template...")
    print("Be sure to insert your IDs into the file into the correct locations.")
    config = {
        "ownerID": "insert-your-user-ID-here",
        "token": "insert-bot-token-here"
    }
    with open('data/config.json', "w+") as configFile:
        json.dump(config, configFile, indent=4)
    exit()
try:
    config = json.load(configFile)
except:
    print("There seems to be an issue with the config.json file. Couldn't be read as json.")
    print("Ensure the file is valid json.")
    exit()
configFile.close()

# Query Bingo Database for Count
countPayload = {'count': True}
count = int(requests.get('http://localhost/michaeldoescoding/projects/pokemon/nuzlockebingo/ctrlpanel/index.php', params=countPayload).text)

# Establish Connection to Database
database = apsw.Connection("data/db.sqlite")
dbCursor = database.cursor()

# Helper Functions
async def logMessage(guild, defaultChannel, message):
    loggingID = list(dbCursor.execute("select LoggingChannelID from flags where ServerID = ?", (guild.id, )))
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

async def canUseAdminCommand(guild, channel, user):
    adminRoles = list(dbCursor.execute("select AdminRoleID from adminRoles where ServerID = ?", (guild.id, )))
    isAdmin = False
    if (len(adminRoles) == 0):
        # If no adminRoles have been set yet, then ensure that the user has Manage Guild permissions?
        isAdmin = user.permissions_in(channel).manage_guild
    else:
        for role in user.roles:
            isAdmin = adminRoles[0].count(str(role.id)) > 0 or isAdmin

    if not isAdmin:
        await channel.send("You need admin permissions to run this command")
    return isAdmin

# Events
@bot.event
async def on_ready():
    print('AssignBot Turned On...')

@bot.event
async def on_member_join(member):
    print("We have triggered the join event")
    joinRoleID = list(dbCursor.execute("select JoinRoleID from flags where ServerID = ?", (member.guild.id, )))
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
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        return

    await logMessage(ctx.guild, ctx.channel, "Bot is shutting down.")
    await bot.close()
    database.close(True)
    print("AssignBot Closed...")

@bot.command()
async def setjoinrole(ctx, joinRoleID):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        return

    joinRole = ctx.guild.get_role(int(joinRoleID))
    if (joinRole == None):
        await logMessage(ctx.guild, ctx.channel, "Provided role not found.")
        return

    serverEntries = list(dbCursor.execute("select ServerID from flags where ServerID = ?", (ctx.guild.id, )))
    if (len(serverEntries) == 0):
        dbCursor.execute("insert into flags (ServerID, JoinRoleID) values (?, ?)", (ctx.guild.id, joinRoleID))
    else:
        dbCursor.execute("update flags set JoinRoleID = ? where ServerID = ?", (joinRoleID, ctx.guild.id))
    await logMessage(ctx.guild, ctx.channel, joinRole.name + " has been set as the auto-join role for " + ctx.guild.name)

@bot.command()
async def addAdminRole(ctx, adminRoleID):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        return

    adminRole = ctx.guild.get_role(int(adminRoleID))
    if (adminRole == None):
        await logMessage(ctx.guild, ctx.channel, "Provided role not found.")
        return

    existingRoles = list(dbCursor.execute("select AdminRoleID from adminRoles where ServerID = ? and AdminRoleID = ?", (ctx.guild.id, adminRoleID)))
    if (len(existingRoles) == 0):
        dbCursor.execute("insert into adminRoles (ServerID, AdminRoleID) values (?, ?)", (ctx.guild.id, adminRoleID))
        await logMessage(ctx.guild, ctx.channel, "Added " + adminRole.name + " as an admin role.")

@bot.command()
async def removeAdminRole(ctx, adminRoleID):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        return

    adminRole = ctx.guild.get_role(int(adminRoleID))
    if (adminRole == None):
        await logMessage(ctx.guild, ctx.channel, "Provided role not found.")
        return

    existingRoles = list(dbCursor.execute("select AdminRoleID from adminRoles where ServerID = ? and AdminRoleID = ?", (ctx.guild.id, adminRoleID)))
    if (len(existingRoles) > 0):
        dbCursor.execute("delete from adminRoles where ServerID = ? and AdminRoleID = ?", (ctx.guild.id, adminRoleID))
        await logMessage(ctx.guild, ctx.channel, "Removed " + adminRole.name + " as an admin role.")

@bot.command()
async def setloggingchannel(ctx):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        return

    serverEntry = list(dbCursor.execute("select ServerID from flags where ServerID = ?", (ctx.guild.id, )))
    if (len(serverEntry) == 0):
        dbCursor.execute("insert into flags (ServerID, LoggingChannelID) values (?, ?)", (ctx.guild.id, ctx.channel.id))
    else:
        dbCursor.execute("update flags set LoggingChannelID = ? where ServerID = ?", (ctx.channel.id, ctx.guild.id))
    await logMessage(ctx.guild, ctx.channel, "#" + ctx.channel.name + " set as the logging channel for AssignBot.")

@bot.command()
async def toggleBingo(ctx):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        return

    allowBingo = list(dbCursor.execute("select AllowBingo from flags where ServerID = ?", (ctx.guild.id, )))
    if (len(allowBingo) == 0):
        dbCursor.execute("insert into flags (ServerID, AllowBingo) values (?, ?)", (ctx.guild.id, 1))
        await ctx.channel.send("Bingo has been activated for this server!")
    elif (allowBingo[0][0] == 0):
        dbCursor.execute("update flags set AllowBingo = ? where ServerID = ?", (1, ctx.guild.id))
        await ctx.channel.send("Bingo has been activated for this server!")
    elif (allowBingo[0][0] != 0):
        dbCursor.execute("update flags set AllowBingo = ? where ServerID = ?", (0, ctx.guild.id))
        await ctx.channel.send("Bingo has been deactivated for this server.")

@bot.command()
async def resetUserBingo(ctx, userID):
    isAdmin = await canUseAdminCommand(ctx.guild, ctx.channel, ctx.author)
    if (not isAdmin):
        return
    user = ctx.guild.get_member(int(userID))
    if (user == None):
        await ctx.channel.send("No user found in this server with ID: " + userID)
        return
    
    dbCursor.execute("delete from bingo where ServerID = ? and UserID = ?", (ctx.guild.id, userID))
    await ctx.channel.send("Bingo Code has been cleared from " + user.name)

@bot.command()
async def bingo(ctx):
    allowBingo = list(dbCursor.execute("select AllowBingo from flags where ServerID = ?", (ctx.guild.id, )))
    if (len(allowBingo) > 0 and allowBingo[0][0] != 0):
        userEntry = list(dbCursor.execute("select BingoCode from bingo where ServerID = ? and UserID = ?", (ctx.guild.id, ctx.author.id)))
        bingoCode = ""
        if (len(userEntry) == 0):
            # generate new code and put it into the table
            pickedEntries = list()
            for index in range(24):
                randEntry = random.randint(0, count)
                while pickedEntries.count(randEntry) > 0:
                    randEntry = random.randint(0, count - 1)
                randEntryHex = hex(randEntry)[2:]
                while len(randEntryHex) < 4:
                    randEntryHex = "0" + randEntryHex
                bingoCode = bingoCode + randEntryHex
                pickedEntries.append(randEntry)
            dbCursor.execute("insert into bingo (ServerID, UserID, BingoCode) values (?, ?, ?)", (ctx.guild.id, ctx.author.id, bingoCode))
        else:
            bingoCode = userEntry[0][0]
        await ctx.channel.send(ctx.author.mention + " Bingo Code: " + bingoCode)

bot.run(config['token'])
