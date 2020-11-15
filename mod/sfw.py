import discord
from discord.ext import commands, tasks
import asyncio
import random
from random import randint
import aiosqlite, os, json

class WarnUser:
    def __init__(self, tag, warnlevel):
        self.tag = tag
        self.warnlevel = warnlevel

    def warn(self):
        self.warnlevel += 1

class Moderator(commands.Cog):
    """Moderators only... A list of mod commands for mods to moderate"""
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    # Start
    async def async_init(self):
        await self.bot.wait_until_ready()

        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS WarnUser(
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
                await db.execute("INSERT OR IGNORE INTO WarnUser (ID, WarnLevel) VALUES (?, ?)",
                (member.id, 0))

            await db.commit()

            async with db.execute("SELECT * FROM WarnUser") as cursor:
                async for row in cursor:
                    x = WarnUser(row[0], row[1])
                    self.users.append(x)

        self.saving.start()

    # Commands

    @commands.command(brief="Checks how many warns the mentioned person has", help="Use this to view the warnstate of a member", usage="@user")
    @commands.has_permissions(administrator=True)
    async def warnstate(self, ctx, member: discord.Member):
        user = await self.getuser(member)
        await ctx.send(f"{member.name} has {user.warnlevel}/4 warns")

    @commands.command(brief="Applies +1 warn to the user mentioned", help="This can be used to warn a user about something that the bot did not catch. Use with disgression", usage="@user reason")
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        user = await self.getuser(member)
        user.warn()
        await member.send(f"You have been warned by {ctx.author.name}. Reason: {reason}\nStrikes: {user.warnlevel} / 4")
        await ctx.send(f"Warned {member.name}. Reason: {reason}. View their warns with p.warnstate")
        await self.log("Warn", f"{member.name} was warned:", str(ctx.author), reason)
        
    @commands.command(brief="This resets the warns that a person has back to 0", help="This sets the warns of a user back to 0.", usage="@user")
    @commands.has_permissions(administrator=True)
    async def resetwarn(self, ctx, member: discord.Member):
        user = await self.getuser(member)
        user.warnlevel = 0
        await ctx.send(f"Reset warns on {member.name} to 0")
        await self.log("Resetwarn", f"{str(member)} had their warns reset", str(ctx.author), reason="None")

    @commands.command(brief="Mutes a user for x seconds", help="Mutes a user for the specified number of seconds", usage="@user duration_in_seconds reason")
    @commands.has_permissions(administrator=True)
    async def timeout(self, ctx, member: discord.Member, time, *, reason):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.send(f"{member.mention} has been timed out for {time} minutes for {reason} by {ctx.author.name}")
        time *= 60

        await asyncio.sleep(time)

        await ctx.send(f"{member.mention}. Your timeout has come to an end. Refrain from having to be timed out again")
        await member.remove_roles(role)
        await self.log("Timeout", f"{str(member)} was timed-out for {time} seconds", str(ctx.author), reason)

    @commands.command(brief="Mutes a user until unmuted", help="Mutes a user until unmuted", usage="@user duration_in_seconds")
    @commands.has_permissions(administrator=True)
    async def mute(self, ctx, member: discord.Member, *, reason):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.send(f"{member.mention} has been muted by {ctx.author}. Reason: {reason}")
        await self.log("Mute", f"{str(member)} was muted", str(ctx.author), reason)

    @commands.command(brief="Unmutes a user that has been muted.", help="Unmutes a muted user", usage="@user")
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(member.roles, name="Muted")
        if not role: await ctx.send("User isn't muted"); return
        await member.remove_roles(role)
        await ctx.send(f"Unmuted {member.mention}. Refrain from having to be muted again")
        await self.log("Unmute", f"{str(member)} was unmuted", str(ctx.author), reason="Null")

        

    @commands.command(brief="Kicks a user", help="Kicks a user from this server", usage="@user reason")
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, *, reason):
        await member.kick(reason=reason)
        await ctx.send(f"{member.name} was kicked from {ctx.guild.name} by {ctx.author.name}. Reason: {reason}")
        await self.log("Kick", f"{str(member)} was kicked", str(ctx.author), reason)

    @commands.command(brief='Bans a user', help="Bans a user from this server", usage="@user reason")
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member:discord.Member, *, reason):
        await member.ban(reason=reason)
        await ctx.send(f"{member.name} was Banned from {ctx.guild.name} by {ctx.author.name}. Reason: {reason}")
        await self.log("Ban", f"{str(member)} was banned", str(ctx.author), reason)
    
    @commands.command(brief="Puts channel in slowmode", help="Use this to apply or disable a channel's slowmode", usage="duration")
    @commands.has_permissions(administrator=True)
    async def slow(self, ctx, duration: int):
        await ctx.channel.edit(slowmode_delay=duration)
        await ctx.send(f"Messages from same user will be in {duration} second intervals")
        await self.log("SLOW", f"{ctx.channel.name} has been slowed to {duration}", str(ctx.author), reason="None")

    @commands.command(brief="Shows the 10 members with the highest warnstate", help="Shows the naughtiest 10 members in the server who have a warnstate")
    @commands.has_permissions(administrator=True)
    async def warned(self, ctx):
        warned = []
        for user in self.users:
            temp = discord.utils.get(ctx.guild.members, id=user.tag)
            if not temp: continue
            if user.warnlevel > 0: warned.append(f"Name: {temp.name}, Warns: {user.warnlevel}")

        if not warned: await ctx.send("Everyone seems to be innocent. Excellent"); return
        await ctx.send("Showing 10 members with highest warns")
        await ctx.send('\n'.join(warned[:10]))

    @commands.command(brief="Resets the warnstate of EVERYONE in the server", help="Clears the warnstate of everyone in the server")
    @commands.has_permissions(administrator=True)
    async def warnreset(self, ctx):
        for user in self.users:
            user.warnlevel = 0

        await ctx.send("Cleared everyone's crimes")
        await self.log("Warn Reset", "Everyone had their crimes cleared", str(ctx.author), reason="Unknown")


    # Events

    with open("swearWords.txt") as f:
        words = f.read()
        profane = words.split("\n")

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot: return
        
        user = await self.getuser(message)
        if not user: return

        for x in ["hentai", "porn"]:
            if x in message.content.lower():
                user.warn()
                await message.channel.send(f"You have been warned for using NSFW content. You are on your {user.warnlevel} / 4 strikes")
                await message.delete()
        
        tempmsg = message.content.lower().split(" ")
        for word in tempmsg:
            if word in self.profane:

                user.warnlevel += 0.5
                msg = await message.channel.send(f"You have been warned for saying {word}. WarnState: {user.warnlevel} / 4 strikes")
                await message.delete()
                await asyncio.sleep(5)
                await msg.delete()
                break

        if user.warnlevel >= 4: 
            await message.author.send(f"You have been muted from PCSG. If you believe it was unfair contact {message.guild.owner}")
            role = discord.utils.get(message.guild.roles, name="Muted")
            await message.author.add_roles(role)
            await message.guild.owner.send(f"{message.author} was muted from PCSG for disobeying rules")

        if message.content.startswith("P."): await message.channel.send("If you are meaning me, my prefix is p. not P.")
        if message.content == "p.": await message.channel.send("Use p.help for a list of my commands.")

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("INSERT OR IGNORE INTO WarnUser (ID, WarnLevel) VALUES (?, ?)", (member.id, 0))

            await db.commit()

        user = await self.getuser(member)
        if user:
            if user.warnlevel >= 4:
                role = discord.utils.get(member.guild.roles, name="Muted")
                await member.add_roles(role)
                await member.send("As your offenses have not been wiped, you are muted.")
        

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            all_cogs = self.bot.cogs
            msg = ctx.message.content.lower().split(".")[1]
            
            potential = []
            for v in all_cogs.values():
                mycommands = v.get_commands()
                if not mycommands: continue
                yes = [name.name for name in mycommands if msg in name.name.lower()]
                if yes:
                    for i in yes: potential.append(i)

            if potential:
                await ctx.send(f"I don't know that command, maybe one of these: {', '.join(potential)}")
            else:
                await ctx.send("Uhm... Try p.help for a list of my commands because I don't know that one")
            return
        
        await ctx.send(error)
        print(error)

    # Tasks
    @tasks.loop(minutes=5)
    async def saving(self):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            for user in self.users:
                await db.execute("INSERT OR REPLACE INTO WarnUser (ID, WarnLevel) VALUES (?, ?)", 
                (user.tag, user.warnlevel))
            await db.commit()
        

    # Functions
    async def getuser(self, m):
        if hasattr(m, "author"):
            toreturn = [x for x in self.users if m.author.id == x.tag]
        else:
            toreturn = [x for x in self.users if m.id == x.tag]
        if toreturn:
            return toreturn[0]
        return None

    logs = []

    if os.path.exists("logs.json"):
        with open("logs.json") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                pass

    async def log(self, modcmd, action, culprit, reason):
        logbed = discord.Embed(
            title="ModLog",
            description="A mod command was used",
            color=randint(0, 0xffffff)
        )
        logbed.add_field(name="Command:", value=modcmd, inline=False)
        logbed.add_field(name="Action", value=action, inline=False)
        logbed.add_field(name="Done By:", value=culprit, inline=False)
        logbed.add_field(name="Reason:", value=reason, inline=False)

        mydict = {"Command":modcmd, "Action":action, "Done By":culprit, "Reason": reason}
        
        self.logs.append(mydict)

        with open("logs.json", "w") as f:
            json.dump(self.logs, f, indent=4) 

def setup(bot):
    bot.add_cog(Moderator(bot))