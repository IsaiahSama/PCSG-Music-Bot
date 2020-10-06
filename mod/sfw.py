import discord
from discord.ext import commands, tasks
import asyncio
import random
from random import randint
import aiosqlite

class WarnUser:
    def __init__(self, name, tag, warnlevel):
        self.name = name
        self.tag = tag
        self.warnlevel = warnlevel

    def warn(self):
        self.warnlevel += 1

class OnlySFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    async def async_init(self):
        await self.bot.wait_until_ready()
        
        await self.setup()

    users = []

    async def setup(self):
        guild = self.bot.get_guild(693608235835326464)
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            for member in guild.members:
                await db.execute("INSERT OR IGNORE INTO WarnUser (Name, ID, WarnLevel) VALUES (?, ?, ?)",
                (member.name, member.id, 0))

            await db.commit()

            async with db.execute("SELECT * FROM WarnUser") as cursor:
                for row in cursor:
                    x = WarnUser(row[0], row[1], row[2])
                    self.users.append(x)

            

    @commands.Cog.listener()
    async def on_message(self, message):
        if ["porn", "hentai"] in message.content:
            await message.channel.send("You have been warned")


def setup(bot):
    bot.add_cog(OnlySFW(bot))