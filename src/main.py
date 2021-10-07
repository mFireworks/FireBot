# Using discord.py for Discord API - https://discordpy.readthedocs.io/en/stable/index.html
import discord
# Using APSW for SQLite Database Management - https://rogerbinns.github.io/apsw/example.html
import apsw

connection = apsw.Connection("data/db.sqlite")
cursor = connection.cursor()

for name in cursor.execute("select ServerID from main"):
    print(name)