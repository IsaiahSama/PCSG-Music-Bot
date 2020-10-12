import discord
from discord.ext import commands, tasks
import random
from random import randint
import asyncio
import aiosqlite


class Person:
    def __init__(self, name, tag, level, exp, expthresh):
        self.name = name
        self.tag = tag
        self.level = level
        self.exp = exp
        self.expthresh = expthresh

    def incexp(self):
        self.exp += 5

    def levelup(self):
        self.exp = 0
        self.expthresh += 50
        self.level += 1

    def didrole(self):
        if self.level % 20 == 0:
            return True
        return False


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    users = []
    roles = []

    # Set up
    async def async_init(self):
        await self.bot.wait_until_ready()
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS Users (
                Name TEXT NOT NULL,
                ID INTEGER PRIMARY KEY UNIQUE NOT NULL,
                Level INTEGER NOT NULL,
                Exp INTEGER NOT NULL,
                ExpThresh INTEGER NOT NULL
                );""")

            await db.commit()
        await self.setup()
        await self.saving.start()

    async def setup(self):
        guild = self.bot.get_guild(693608235835326464)
        self.roles = [role.name for role in guild.roles if role.name.endswith("Learner")]

        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            for member in guild.members:
                if member.bot: continue
                await db.execute("INSERT OR IGNORE INTO Users (Name, ID, Level, Exp, ExpThresh) VALUES (?, ?, ?, ?, ?)",
                (str(member), member.id, 0, 0, 50))

            await db.commit()

            async with db.execute("SELECT * FROM Users") as cursor:
                async for row in cursor:
                    x = Person(row[0], row[1], row[2], row[3], row[4])
                    self.users.append(x)

                print("All users have been added")

    # Commands

    @commands.command()
    async def profile(self, ctx):
        person = await self.getperson(ctx)
        if not person:
            return

        probed = discord.Embed(
            title=f"Showing Profile for {ctx.author}",
            color=randint(0, 0xffffff)
        )

        probed.set_thumbnail(url=ctx.author.avatar_url)
        probed.add_field(name="Name:", value=person.name)
        probed.add_field(name="Level:", value=person.level)
        probed.add_field(name="Exp:", value=f"{person.exp}/{person.expthresh}")

        await ctx.send(embed=probed)

    @commands.command()
    async def rank(self, ctx):
        person = await self.getperson(ctx)
        x = self.users
        x = sorted(x, key= lambda item: (item.level, item.exp), reverse=True)

        rk = x.index(person)
        await ctx.send(f"You are ranked {rk + 1} of {len(x)} members")


    @commands.command()
    async def top(self, ctx):
        x = self.users
        x = sorted(x, key= lambda item: (item.level, item.exp), reverse=True)

        y = x[:5]

        embed = discord.Embed(
            title=f"Showing top 5 Studious Learners",
            color=randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=ctx.guild.icon_url)
        for u in y:
            embed.add_field(name=u.name, value=f"Level: {u.level} Exp: {u.exp}", inline=False)

        await ctx.send(embed=embed)
    # Listeners

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("INSERT OR IGNORE INTO Users (Name, ID, Level, Exp, ExpThresh) VALUES (?, ?, ?, ?, ?)",
            (member.name, member.id, 0, 0, 50))

    @commands.Cog.listener()
    async def on_memeber_remove(self, member:discord.Member):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("DELETE * FROM Users WHERE ID = ?", (member.id,))

            await db.commit()


    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.author.bot: return

        person = await self.getperson(message)
        if not person:
            return

        person.incexp()
        if person.exp >= person.expthresh:
            person.levelup()

            embed = discord.Embed(
                title="LEVEL UP",
                description=f"{message.author.mention} has reached level {person.level}. Keep Studying hard",
                color=randint(0, 0xffffff)
            )
            if person.didrole():
                role_to_give = self.roles[(person.level / 20) - 1]
                if person.level / 20 >= len(self.roles):
                    return
                await message.author.add_role(role_to_give)

                embed.add_field(name="New role", value=f"Congrats {message.author.name}. You now have the role of {role_to_give.name}")

            await message.channel.send(embed=embed)
    
    # Tasks    
    @tasks.loop(minutes=5)
    async def saving(self):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            for member in self.users:
                await db.execute("INSERT OR REPLACE INTO Users (Name, ID, Level, Exp, ExpThresh) VALUES (?, ?, ?, ?, ?)",
                (member.name, member.tag, member.level, member.exp, member.expthresh))

            await db.commit()

        # pass

    # Functions
    async def getperson(self, m):
        toreturn = [x for x in self.users if m.author.id == x.tag]
        if not toreturn:
            await m.channel.send(f"Something went wrong getting your user. Try again later or contact Mods")
            return None
        return toreturn[0]


def setup(bot):
    bot.add_cog(Leveling(bot))
