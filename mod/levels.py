import asyncio
import discord
from discord import user
from discord.errors import HTTPException
from discord.ext import commands
from random import randint
import aiosqlite
from mydicts import *


class Person:
    def __init__(self, tag, level, exp, expthresh):
        self[columns['ID']] = tag
        self[columns['LEVEL']] = level
        self[columns['EXP']] = exp
        self[columns['EXPTHRESH']] = expthresh

    def incexp(self):
        self[columns['EXP']] += 5

    def levelup(self):
        self[columns['EXP']] = 0
        self[columns['EXPTHRESH']] += 50
        self[columns['LEVEL']] += 1

    def didrole(self):
        if self[columns['LEVEL']] > 1 and self[columns['LEVEL']] % 20 == 0:
            return True
        return False

columns = {
    "ID": 0,
    "LEVEL": 1,
    "EXP": 2,
    "EXPTHRESH":3
}

class Progression(commands.Cog):
    """Competition is good :) and these commands will let you know all that's going on competitively. Strive to be #1"""
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    roles = ["SEASONED", "EXPERIENCED", "ADVANCED", "ELITIST"]

    # Set up
    async def async_init(self):
        await self.bot.wait_until_ready()
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS StudentTable (
                ID INTEGER PRIMARY KEY UNIQUE NOT NULL,
                Level INTEGER NOT NULL,
                Exp INTEGER NOT NULL,
                ExpThresh INTEGER NOT NULL
                );""")

            await db.commit()
        await self.setup()

    async def setup(self):
        guild = self.bot.get_guild(guild_id)

        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            for member in guild.members:
                if member.bot: continue
                await db.execute("INSERT OR IGNORE INTO StudentTable (ID, Level, Exp, ExpThresh) VALUES (?, ?, ?, ?)",
                (member.id, 0, 0, 50))

            await db.commit()

    # Commands

    @commands.command(brief="Shows your PCSG Student Profile", help="Used to view a PCSG Student Profile, either yours or the person you @mention", usage="optional[@mention]")
    async def profile(self, ctx, member:discord.Member=None):
        student = member or ctx.author
        person = await self.getuser(student)

        if not person:
            return

        user_subjects = [ctx.guild.get_role(role.id).mention for role in student.roles if role.name.lower() in list(reactions["CSEC"].values()) or role.name.lower() in list(reactions["CAPE"].values())]

        embed = discord.Embed(
            title=f"Showing Profile for {student}",
            color=randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=student.avatar_url)
        embed.add_field(name="Name:", value=student.name)
        embed.add_field(name="Level:", value=person[columns['LEVEL']])
        embed.add_field(name="Exp:", value=f"{person[columns['EXP']]}/{person[columns['EXPTHRESH']]}")
        embed.add_field(name="Highest Role:", value=student.top_role)
        embed.add_field(name="Subjects:", value=''.join(user_subjects[:25]) or "No subjects")
        embed.add_field(name="On Cooldown:", value=await self.on_chilldown(person))

        await ctx.send(embed=embed)

    @commands.command(brief="Shows your rank", help="Shows your rank in terms of leveling with your fellow students")
    async def rank(self, ctx, member:discord.Member=None):
        student = member or ctx.author
        person = await self.getuser(student)
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        cursor = await db.execute("SELECT * FROM StudentTable")
        rows = await cursor.fetchall()
        await db.close()
        rows.append(person)
        rows = sorted(rows, key= lambda x: (x[columns['LEVEL']], x[columns['EXP']]), reverse=True)

        rank = rows.index(person)
        await ctx.send(f"{student.display_name} is ranked {rank} of {len(rows)} members")


    @commands.command(brief="Shows top 5 studious learners", help="Used to see the top 5 most active users")
    async def top(self, ctx):
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        cursor = await db.execute("SELECT * FROM StudentTable")
        students = await cursor.fetchall()
        await db.close()
        
        students = sorted(students, key= lambda x: (x[columns['LEVEL']], x[columns['EXP']]), reverse=True)

        embed = discord.Embed(
            title=f"Showing top 5 Studious Learners",
            color=randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=ctx.guild.icon_url)
        for student in students[:5]:
            name = ctx.guild.get_member(student[columns['ID']]).name
            embed.add_field(name=name, value=f"Level: {student[columns['LEVEL']]} Exp: {student[columns['EXP']]}", inline=False)

        await ctx.send(embed=embed)
    # Listeners

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("INSERT OR IGNORE INTO StudentTable (ID, Level, Exp, ExpThresh) VALUES (?, ?, ?, ?)",
            (member.id, 0, 0, 50))

    @commands.Cog.listener()
    async def on_memeber_remove(self, member:discord.Member):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("DELETE FROM StudentTable WHERE ID = ?", (member.id,))

            await db.commit()

    on_cooldown = []

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        if message.content.lower().startswith("p."): return

        student = await self.getuser(message.author)
        if not student: return

        if await self.on_chilldown(student):
            return
        
        student[columns["EXP"]] += 5

        if student[columns["EXP"]] >= student[columns["EXPTHRESH"]]:
            student[columns['EXP']] = 0
            student[columns['EXPTHRESH']] += 50
            student[columns['LEVEL']] += 1

            embed = discord.Embed(
                title="LEVEL UP",
                description=f"{message.author.mention} has reached level {student[columns['LEVEL']]}. Keep Studying hard",
                color=randint(0, 0xffffff)
            )

            if student[columns['LEVEL']] > 1 and student[columns['LEVEL']] % 20 == 0:

                role_to_give = discord.utils.get(message.guild.roles, id=all_roles[self.roles[(student[columns['LEVEL']] // 20) - 1]])
                
                if not role_to_give: return

                await message.author.add_roles(role_to_give)

                embed.add_field(name="New role", value=f"Congrats {message.author.mention}. You now have the role of {role_to_give.mention}")

            await message.channel.send(embed=embed)

        self.on_cooldown.append(student)
        await self.update_user(student)
        await asyncio.sleep(10)
        self.on_cooldown.remove(student)

    
    # Functions
    async def getuser(self, m):
        db = await aiosqlite.connect("PCSGDB.sqlite3")

        cursor = await db.execute("SELECT * FROM StudentTable WHERE (ID) == ?", (m.id, ))

        row = await cursor.fetchone()

        await db.close()

        if row:
            return list(row)
        return None

    async def on_chilldown(self, user):
        if [person for person in self.on_cooldown if user[columns["ID"]] == person[columns["ID"]]]:
            return True
        return False

    async def update_user(self, user):
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        await db.execute("UPDATE StudentTable SET LEVEL = ?, EXP = ?, EXPTHRESH = ? WHERE ID == ?", (user[columns["LEVEL"]], user[columns["EXP"]], user[columns["EXPTHRESH"]], user[columns["ID"]]))
        await db.commit()
        await db.close()


def setup(bot):
    bot.add_cog(Progression(bot))
