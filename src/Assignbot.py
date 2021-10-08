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

# Events
@bot.event
async def on_ready():
    print('AssignBot Turned On...')

@bot.event
async def on_member_join(member):
    print("We have triggered the join event")
    joinRole = list(dbCursor.execute("select JoinRoleID from main where ServerID = ?", (member.guild.id, )))
    if (len(joinRole) == None or len(joinRole) > 1):
        print(member.guild.name + " doesn't have a join role set")
        return

    role = discord.utils.get(member.guild.roles, id=int(joinRole[0][0]))
    await member.add_roles(role)
    print("Sent " + member.name + " to auto-join role " + role.name)

# Commands
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def shutdown(ctx):
    if (ctx.author.id != int(config['ownerID'])):
        return
    await ctx.send("Bot is shutting down.")
    await bot.close()
    database.close(True)
    print("AssignBot Closed...")

@bot.command()
async def setjoinrole(ctx, joinRoleID):
    joinRole = ctx.guild.get_role(int(joinRoleID))
    if (joinRole == None):
        await ctx.send("Provided role not found.")
        return

    serverEntries = list(dbCursor.execute("select ServerID from main where ServerID = ?", (ctx.guild.id, )))
    if (len(serverEntries) == 0):
        dbCursor.execute("insert into main (ServerID, JoinRoleID) values (?, ?)", (ctx.guild.id, joinRoleID))
    else:
        dbCursor.execute("update main set JoinRoleID = ? where ServerID = ?", (joinRoleID, ctx.guild.id))
    await ctx.send(joinRole.name + " has been set as the auto-join role for " + ctx.guild.name)


bot.run(config['token'])
