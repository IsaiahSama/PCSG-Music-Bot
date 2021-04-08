import discord, time, asyncio, random, aiosqlite, os, json, sqlite3, time
from discord.ext import commands, tasks
from random import randint

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
                    userdict = {"TAG": row[0], "WARNLEVEL":row[1]}
                    self.users.append(userdict)

        self.saving.start()

    # Commands

    @commands.command(brief="Checks how many warns the mentioned person has", help="Use this to view the warnstate of a member", usage="@user")
    @commands.has_permissions(administrator=True)
    async def warnstate(self, ctx, member: discord.Member):
        user = await self.getuser(member)
        await ctx.send(f"{member.name} has {user['WARNLEVEL']}/4 warns")

    @commands.command(brief="Applies +1 warn to the user mentioned", help="This can be used to warn a user about something that the bot did not catch. Use with disgression", usage="@user reason")
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        user = await self.getuser(member)
        user["WARNLEVEL"] += 1
        await member.send(f"You have been warned by {ctx.author.name}. Reason: {reason}\nStrikes: {user['WARNLEVEL']} / 4")
        await ctx.send(f"Warned {member.name}. Reason: {reason}. View their warns with p.warnstate")
        await self.log("Warn", f"{member.name} was warned:", str(ctx.author), reason)
        
    @commands.command(brief="This resets the warns that a person has back to 0", help="This sets the warns of a user back to 0.", usage="@user")
    @commands.has_permissions(administrator=True)
    async def resetwarn(self, ctx, member: discord.Member):
        user = await self.getuser(member)
        user['WARNLEVEL'] = 0
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
            temp = discord.utils.get(ctx.guild.members, id=user['TAG'])
            if not temp: continue
            if user['WARNLEVEL'] > 0: warned.append(f"Name: {temp.name}, Warns: {user['WARNLEVEL']}")

        if not warned: await ctx.send("Everyone seems to be innocent. Excellent"); return
        await ctx.send("Showing 10 members with highest warns")
        await ctx.send('\n'.join(warned[:10]))

    @commands.command(brief="Resets the warnstate of EVERYONE in the server", help="Clears the warnstate of everyone in the server")
    @commands.has_permissions(administrator=True)
    async def warnreset(self, ctx):
        for user in self.users:
            user['WARNLEVEL'] = 0

        await ctx.send("Cleared everyone's crimes")
        await self.log("Warn Reset", "Everyone had their crimes cleared", str(ctx.author), reason="Unknown")

    @commands.command(brief="Deletes x amount of messages", help="Used to bulk delete messages")
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, amount:int):
        await ctx.channel.purge(limit=amount)

    # Events

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        changed, embed = await self.was_changed(before, after)
        if not embed: return

        if changed == "nickname":
            channel = before.guild.get_channel(785986850736963675)
        elif changed == "roles":
            channel = before.guild.get_channel(785986876531015711)
        else: return

        embed.set_footer(text=f"User ID: {before.id}")

        await channel.send(embed=embed)
        

    async def was_changed(self, before, after):
        if not before.nick == after.nick:
            if not after.nick: after.nick = after.name
            embed = discord.Embed(
                title="Wait... so they want to have a nickname?",
                description=f"{str(before)} would like to be known as {after.nick}",
                color=randint(0, 0xffffff)
            )
            return "nickname", embed

        if not before.roles == after.roles:
            value = await before.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten()
            value = value[0]
            try:
                initial = value.before.roles[0].name
            except IndexError:
                initial = "Received the role"
            try:
                final = value.after.roles[0].name
            except IndexError:
                final = "was removed"
            
            embed = discord.Embed(
                title=f"Role updates for {before.name}/{before.nick}",
                description=f"{str(value.user)} changed {value.target}'s roles. {initial} {final}",
                color=randint(0, 0xffffff)
            )

            return "roles", embed

        return None, None

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        embed = discord.Embed(
            title=f"{message.author} had a deleted message in {message.channel.name}",
            description=message.content,
            color=randint(0, 0xffffff)
        )
        channel = message.guild.get_channel(785993210522107925)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messagelist):
        embed = discord.Embed(
            title="Bulk Deletion",
            description=f"{len(messagelist)} messages were bulk deleted.",
            color=randint(0, 0xffffff)
        )

        for msg in messagelist[:24]:
            embed.add_field(name=f"Deleted from {msg.channel.name}", value=f"{msg.content[:550]} ...")

        await messagelist[0].guild.get_channel(786003742813192233).send(embed=embed)
    

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
                user["WARNLEVEL"] += 1
                await message.channel.send(f"You have been warned for using NSFW content. You are on your {user['WARNLEVEL']} / 4 strikes")
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass
        
        tempmsg = message.content.lower().split(" ")
        for word in tempmsg:
            if word in self.profane:

                user['WARNLEVEL'] += 0.5
                msg = await message.channel.send(f"You have been warned for saying {word}. WarnState: {user['WARNLEVEL']} / 4 strikes")
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass
                await asyncio.sleep(5)
                await msg.delete()
                break

        if user['WARNLEVEL'] >= 4: 
            await message.author.send(f"You have been muted from PCSG. If you believe it was unfair contact {message.guild.owner}")
            role = discord.utils.get(message.guild.roles, name="Muted")
            await message.author.add_roles(role)
            await message.guild.owner.send(f"{message.author} was muted from PCSG for disobeying rules")

        if message.content == "p.": await message.channel.send("Use p.help for a list of my commands.")

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        if member.bot: return
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("INSERT OR IGNORE INTO WarnUser (ID, WarnLevel) VALUES (?, ?)", (member.id, 0))

            await db.commit()

        user = await self.getuser(member)
        if user:
            if user['WARNLEVEL'] >= 4:
                role = discord.utils.get(member.guild.roles, name="Muted")
                await member.add_roles(role)
                await member.send("As your offenses have not been wiped, you are muted.")

        embed = discord.Embed(
            title="Member join",
            description=f"{str(member.name)} has just joined the server.",
            color=randint(0, 0xffffff)
        )

        embed.add_field(name="Account Creation Date", value=member.created_at.strftime("%d/%m/%y"))
        embed.add_field(name="Joined at", value=time.ctime())
        await member.guild.get_channel(786016910668070952).send(embed=embed)
        role = discord.utils.get(member.guild.roles, id=755633133600112651)
        role2 = discord.utils.get(member.guild.roles, id=762190942316134400)
        role_channel = member.guild.get_channel(762068938686595152)
        intro_channel = member.guild.get_channel(762060265520365568)

        await member.add_roles(role, role2)
        humans = [member for member in member.guild.members if not member.bot]
        if human_count := len(humans) % 100 == 0:
            await member.guild.get_channel(700214669003980801).send(f"CONGRATULATIONS TO {member.mention} FOR BEING THE {human_count}th HUMAN TO JOIN THE PCSG FAMILY!!!")
        await member.guild.get_channel(700214669003980801).send(f"Welcome to the **PCSG FAMILY** {member.mention}:heart: \nThis server is designed to help you understand how you study best and achieve every **STUDY-GOAL!!!** :partying_face: Press here: {intro_channel.mention} and introduce yourself, then press here: {role_channel.mention} to start getting your roles.")


    @commands.Cog.listener()
    async def on_member_ban(self, member):
        bann = await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        ban = bann[0]

        embed = discord.Embed(
            title="I see... Now you're banned",
            description=f"{str(ban.target)} has been banned by {str(ban.user)}",
            color=randint(0, 0xffffff)
        )

        embed.add_field(name="Reason", value=ban.reason)
        embed.set_footer(text=f"Target ID {ban.target.id}. Banner ID {ban.user.id}")

        await member.guild.get_channel(786016910668070952).send(embed=embed)

    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="Leaving",
            description=f"It would seem as though {str(member)} has left the server",
            color=randint(0, 0xffffff)
        )

        entry = await member.guild.audit_logs(limit=1).flatten()
        entry = entry[0]
        if entry.action is discord.AuditLogAction.kick:
            embed.add_field(name=":o , It was a kick", value=f"{str(entry.target)} was kicked by {str(entry.user)} for {entry.reason}")
        
        await member.guild.get_channel(786016910668070952).send(embed=embed)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.embeds: return
        embed = discord.Embed(
            description=f"{str(before.author)} made an edit to a message in {after.channel.name}",
            title="A message has been edited.",
            color=randint(0, 0xffffff)
        )

        embed.add_field(name="Before", value=before.content or "Unknown")
        embed.add_field(name="After", value=after.content or "Unknown", inline=False)
        embed.add_field(name="Jump URL", value=after.jump_url)
        embed.set_footer(text=f"User ID: {before.author.id}")

        await before.guild.get_channel(785993210522107925).send(embed=embed)
        


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error_channel = ctx.guild.get_channel(828638567236108308)
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
        await error_channel.send(error)


    # Tasks
    @tasks.loop(seconds=250)
    async def saving(self):
        try:
            async with aiosqlite.connect("PCSGDB.sqlite3") as db:
                for user in self.users:
                    await db.execute("INSERT OR REPLACE INTO WarnUser (ID, WarnLevel) VALUES (?, ?)", 
                    (user['TAG'], user['WARNLEVEL']))
                await db.commit()
        except sqlite3.OperationalError:
            print("Database is in use.")
            await asyncio.sleep(120)
            self.saving.restart()
        

    # Functions
    async def getuser(self, m):
        if hasattr(m, "author"):
            toreturn = [x for x in self.users if m.author.id == x['TAG']]
        else:
            toreturn = [x for x in self.users if m.id == x['TAG']]
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

        mydict = {"Command":modcmd, "Action":action, "Done By":culprit, "Reason": reason, "Time": time.ctime()}
        
        self.logs.append(mydict)

        with open("logs.json", "w") as f:
            json.dump(self.logs, f, indent=4)

def setup(bot):
    bot.add_cog(Moderator(bot))