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

    # Start
    async def async_init(self):
        await self.bot.wait_until_ready()

        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS WarnUser(
                Name Text NOT NULL,
                ID INTEGER PRIMARY KEY UNIQUE NOT NULL,
                WarnLevel INTEGER NOT NULL
            )""")

            await db.commit()

        await self.setup()

    users = []

    async def setup(self):
        guild = self.bot.get_guild(693608235835326464)
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            for member in guild.members:
                if member.bot: continue
                await db.execute("INSERT OR IGNORE INTO WarnUser (Name, ID, WarnLevel) VALUES (?, ?, ?)",
                (member.name, member.id, 0))

            await db.commit()

            async with db.execute("SELECT * FROM WarnUser") as cursor:
                async for row in cursor:
                    x = WarnUser(row[0], row[1], row[2])
                    self.users.append(x)

        await self.saving.start()

    # Commands

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warnstate(self, ctx, member: discord.Member):
        user = await self.getuser(member)
        await ctx.send(f"{member.name} has {user.warnlevel}/4 warns")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        user = await self.getuser(member)
        user.warn()
        await member.send(f"You have been warned by {ctx.author.name}. Reason: {reason}\nStrikes: {user.warnlevel} / 4")
        await ctx.send(f"Warned {member.name}. Reason: {reason}. View their warns with p.warnstate")
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetwarn(self, ctx, member: discord.Member):
        user = await self.getuser(member)
        user.warnlevel = 0
        await ctx.send(f"Reset warns on {member.name} to 0")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def mute(self, ctx, member: discord.Member, time=5):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.send(f"{member.mention} has been muted for {time} minutes")
        time *= 60

        await asyncio.sleep(time)

        await ctx.send(f"{member.mention}. Your mute has come to an end. Refrain from having to be muted again")
        await member.remove_roles(role)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, *, reason):
        await member.kick(reason=reason)
        await ctx.send(f"{member.name} was kicked from {ctx.guild.name} by {ctx.author.name}. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member:discord.Member, *, reason):
        await member.ban(reason=reason)
        await ctx.send(f"{member.name} was Banned from {ctx.guild.name} by {ctx.author.name}. Reason: {reason}")
    
    # Events

    with open("swearWords.txt") as f:
        words = f.read()
        profane = words.split(", ")

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot: return
        
        user = await self.getuser(message)

        for x in ["hentai", "porn"]:
            if x in message.content.lower():
                user.warn()
                await message.channel.send(f"You have been warned for using NSFW content. You are on your {user.warnlevel} / 4 strikes")
                await message.delete()
        
        tempmsg = message.content.lower().split(" ")
        for l in tempmsg:
            if l in self.profane:

                user.warnlevel += 0.5
                msg = await message.channel.send(f"You have been warned for saying {l}. WarnState: {user.warnlevel} / 4 strikes")
                await message.delete()
                await asyncio.sleep(5)
                await msg.delete()
                break

        if user.warnlevel >= 4: 
            await message.author.kick(reason="Disobeyed laws")
            await message.guild.owner(f"{message.author} was kicked from PCSG")

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("INSERT OR IGNORE INTO WarnUser (Name, ID, WarnLevel) VALUES (?, ?, ?)", (member.name, member.id, 0))

            await db.commit()

        user = await self.getuser(member)
        if user:
            if user.warnlevel >= 4:
                role = discord.utils.get(member.guild.roles, name="Muted")
                await member.add_roles(role)
                await member.send("As your offenses have not been wiped, you are muted.")
        

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(error)

    # Tasks
    @tasks.loop(minutes=5)
    async def saving(self):
        # async with aiosqlite.connect("PCSGDB.sqlite3") as db:
        #     for user in self.users:
        #         await db.execute("INSERT OR REPLACE INTO WarnUser (Name, ID, WarnLevel) VALUES (?, ?, ?)", 
        #         (user.name, user.tag, user.warnlevel))

        #     await db.commit()
        pass

    # Functions
    async def getuser(self, m):
        if hasattr(m, "author"):
            toreturn = [x for x in self.users if m.author.id == x.tag]
        else:
            toreturn = [x for x in self.users if m.id == x.tag]
        if toreturn:
            return toreturn[0]
        print("Something went wrong")
        return None

def setup(bot):
    bot.add_cog(OnlySFW(bot))