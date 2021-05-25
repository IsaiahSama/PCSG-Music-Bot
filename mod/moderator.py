import discord, time, asyncio, aiosqlite, sqlite3, time
from discord import utils
from discord.ext.commands.cooldowns import BucketType
from mydicts import *
from discord.ext import commands, tasks
from random import randint
from re import compile

class Moderator(commands.Cog):
    """These commands assist our mods with their job. Better be good... I'm also watching you"""
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

            await db.execute("CREATE TABLE IF NOT EXISTS MonitorTable(ID INTEGER PRIMARY KEY UNIQUE NOT NULL)")

            await db.commit()

        await self.setup()


    async def setup(self):
        guild = self.bot.get_guild(guild_id)
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        for member in guild.members:
            if member.bot: continue
            await db.execute("INSERT OR IGNORE INTO WarnUser (ID, WarnLevel) VALUES (?, ?)",
            (member.id, 0))

        await db.commit()
        await db.close()

    # Commands

    @commands.command(brief="Checks how many warns the mentioned person has", help="Use this to view the warnstate of a member", usage="@user")
    @commands.has_permissions(administrator=True)
    async def warnstate(self, ctx, member: discord.Member):
        user = await self.getuser(member)
        await ctx.send(f"{member.name} has {user[1]}/4 warns")

    @commands.command(brief="Applies +1 warn to the user mentioned", help="This can be used to warn a user about something that the bot did not catch. Use with disgression", usage="@user reason")
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        user = await self.getuser(member)
        user[1] += 1
        await member.send(f"You have been warned by {ctx.author.name}. Reason: {reason}\nStrikes: {user[1]} / 4")
        await ctx.send(f"Warned {member.name}. Reason: {reason}. View their warns with p.warnstate")
        await log("Warn", f"{member.name} was warned:", str(ctx.author), reason)
        await self.update_warns(member.id, user[1])
        
    @commands.command(brief="This resets the warns that a person has back to 0", help="This sets the warns of a user back to 0.", usage="@user")
    @commands.has_permissions(administrator=True)
    async def resetwarn(self, ctx, member: discord.Member):
        user = await self.getuser(member)
        user[1] = 0
        await ctx.send(f"Reset warns on {member.name} to 0")
        await log("Resetwarn", f"{str(member)} had their warns reset", str(ctx.author), reason="None")
        await self.update_warns(member.id, user[1])

    @commands.command(brief="Mutes a user for x seconds", help="Mutes a user for the specified number of seconds", usage="@user duration_in_seconds reason")
    @commands.has_permissions(administrator=True)
    async def timeout(self, ctx, member: discord.Member, time, *, reason):
        role = discord.utils.get(ctx.guild.roles, id=all_roles["MUTED"])
        await member.add_roles(role)
        await ctx.send(f"{member.mention} has been timed out for {time} minutes for {reason} by {ctx.author.name}")
        await log("Timeout", f"{str(member)} was timed-out for {time} seconds", str(ctx.author), reason)
        time *= 60

        await asyncio.sleep(time)

        await ctx.send(f"{member.mention}. Your timeout has come to an end. Refrain from having to be timed out again")
        await member.remove_roles(role)

    @commands.command(brief="Mutes a user until unmuted", help="Mutes a user until unmuted", usage="@user duration_in_seconds")
    @commands.has_permissions(administrator=True)
    async def mute(self, ctx, member: discord.Member, *, reason):
        role = discord.utils.get(ctx.guild.roles, id=all_roles["MUTED"])
        await member.add_roles(role)
        await ctx.send(f"{member.mention} has been muted by {ctx.author}. Reason: {reason}")
        await log("Mute", f"{str(member)} was muted", str(ctx.author), reason)

    @commands.command(brief="Unmutes a user that has been muted.", help="Unmutes a muted user", usage="@user")
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(member.roles, id=all_roles["MUTED"])
        if not role: await ctx.send("User isn't muted"); return
        await member.remove_roles(role)
        await ctx.send(f"Unmuted {member.mention}. Refrain from having to be muted again")
        await log("Unmute", f"{str(member)} was unmuted", str(ctx.author), reason="Null")

    @commands.command(brief="Kicks a user", help="Kicks a user from this server", usage="@user reason")
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, *, reason):
        await member.kick(reason=reason)
        await ctx.send(f"{member.name} was kicked from {ctx.guild.name} by {ctx.author.name}. Reason: {reason}")
        await log("Kick", f"{str(member)} was kicked", str(ctx.author), reason)

    @commands.command(brief='Bans a user', help="Bans a user from this server", usage="@user reason")
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member:discord.Member, *, reason):
        await member.ban(reason=reason)
        await ctx.send(f"{member.name} was Banned from {ctx.guild.name} by {ctx.author.name}. Reason: {reason}")
        await log("Ban", f"{str(member)} was banned", str(ctx.author), reason)
    
    @commands.command(brief="Puts channel in slowmode", help="Use this to apply or disable a channel's slowmode", usage="duration")
    @commands.has_permissions(administrator=True)
    async def slow(self, ctx, duration: int):
        await ctx.channel.edit(slowmode_delay=duration)
        await ctx.send(f"Messages from same user will be in {duration} second intervals")
        await log("SLOW", f"{ctx.channel.name} has been slowed to {duration}", str(ctx.author), reason="None")

    @commands.command(brief="Shows the 10 members with the highest warnstate", help="Shows the naughtiest 10 members in the server who have a warnstate")
    @commands.has_permissions(administrator=True)
    async def warned(self, ctx):
        warned = []
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        cursor = await db.execute("SELECT * FROM WarnUser")
        users = await cursor.fetchall()
        for user in users:
            temp = discord.utils.get(ctx.guild.members, id=user[0])
            if not temp: continue
            if user[1] > 0: warned.append(f"Name: {temp.name}, Warns: {user[1]}")
        
        await db.close()

        if not warned: await ctx.send("Everyone seems to be innocent. Excellent"); return
        warned.sort()
        await ctx.send("Showing 10 members with highest warns")
        await ctx.send('\n'.join(warned[:10]))

    @commands.command(brief="Resets the warnstate of EVERYONE in the server", help="Clears the warnstate of everyone in the server")
    @commands.has_permissions(administrator=True)
    async def warnreset(self, ctx):
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        cursor = await db.execute("SELECT * FROM WarnUser WHERE WarnLevel > 0")
        warned = await cursor.fetchall()
        if not warned:
            await ctx.send("Everyone is clean")
            return

        for person in warned:
            await db.execute("UPDATE WarnUser SET WarnLevel = 0 where (ID) == ?", (person[0],))
        await db.commit()
        await db.close()
        await ctx.send("Cleared everyone's crimes")
        await log("Warn Reset", "Everyone had their crimes cleared", str(ctx.author), reason="For purity.")


    @commands.command(brief="Deletes x amount of messages", help="Used to bulk delete messages")
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, amount:int):
        await ctx.channel.purge(limit=amount)

    # Events

    

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot: return
        
        target = await self.is_monitored(message.author)
        if target:
            monitor_channel = message.guild.get_channel(channels["MONITOR"])
            await monitor_channel.send(f"{message.author.mention} in {message.channel.mention}: {message.content}")
            

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        if member.bot: return
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        await db.execute("INSERT OR IGNORE INTO WarnUser (ID, WarnLevel) VALUES (?, ?)", (member.id, 0))
        await db.commit()
        await db.close()
        
        user = await self.getuser(member)
        if user:
            if user[1] >= 4:
                role = discord.utils.get(member.guild.roles, id=all_roles["MUTED"])
                await member.add_roles(role)
                try:
                    await member.send("As your offenses have not been wiped, you are muted.")
                except:
                    await member.guild.get_channel(channels["WELCOME_CHANNEL"]).send(f"{member.mention}. As your offenses have not been cleared, you are muted")

        embed = discord.Embed(
            title="Member join",
            description=f"{str(member.name)} has just joined the server.",
            color=randint(0, 0xffffff)
        )

        embed.add_field(name="Account Creation Date", value=member.created_at.strftime("%d/%m/%y"))
        embed.add_field(name="Joined at", value=time.ctime())
        await member.guild.get_channel(channels["JOIN_LEAVES"]).send(embed=embed)

        human_count = sum(not human.bot for human in member.guild.members)

        if human_count % 100 == 0:
            await member.guild.get_channel(channels["WELCOME_CHANNEL"]).send(f"CONGRATULATIONS TO {member.mention} FOR BEING THE {human_count}th HUMAN TO JOIN THE PCSG FAMILY!!!")
        
        await member.guild.get_channel(channels["WELCOME_CHANNEL"]).send(
f"""Welcome {member.mention} to the <:PCSGLETTERSWITHOUTBACKGROUND:828392100729978900> Family! <a:catholdheart:830938992081371157> You're the **{sum(not user.bot for user in member.guild.members)}th Family Member <:holdheart:830939097518178375>**
Thank You for joining **The Study-Goals' E-School <a:movingstar:830939250513674311>**

We look forward to studying with you, Newbie E-Schooler! <a:party:830939382944628766>
""")
        await member.guild.get_channel(channels["WELCOME_CHANNEL"]).send("https://cdn.discordapp.com/attachments/813888001775370320/831305455237988402/WELCOME_TO_STUDY_GOALS_E-SCHOOL_4.gif")
        name_channel = member.guild.get_channel(834839533978779718)
        await name_channel.send(f"Hello {member.mention}, what is your name.")

    @commands.command(brief="Moves all members in the user's vc to another one", help="Used to move all members in the same vc as the user to another vc, whose id is specified", usage="name_or_id_of_vc_to_move_to")
    @commands.has_guild_permissions(move_members=True)
    async def moveto(self, ctx, *, name_or_id_of_vc):
        if not ctx.author.voice.channel:
            await ctx.send("You are not currently connected to a voice channel")
            return 
        
        if not name_or_id_of_vc.isnumeric():
            vc_name = name_or_id_of_vc
            channels = [channel for channel in ctx.guild.channels if hasattr(channel, "connect") and vc_name.lower() in channel.name.lower()]
            if not channels:
                await ctx.send("Could not find any channels with that name. Double check spelling.")
                return

            if len(channels) > 1:
                await ctx.send("You have more than one channel matching the name given. Use the command again, but use the id of the channel instead provided below")
                channel_msg = ""
                for channel in channels:
                    channel_msg += f"`{channel.name}: {channel.id}`\n"
                
                await ctx.send(channel_msg)
                return

            channel = channels[0]
            
        elif name_or_id_of_vc.isnumeric():
            vc_id = int(name_or_id_of_vc)
            channel = utils.get(ctx.guild.channels, id=vc_id)
            if not channel:
                await ctx.send("There is no channel in this server with that id.")
                return

        else:
            await ctx.send("The text you entered, I do not recognise.")
            return 

        confirmation = ["✅", "❌"]

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in confirmation

        msg = await ctx.send(f"Are you sure you want to move all {len(ctx.author.voice.channel.members)} members of your voice channel to {channel.name}")
        for emoji in confirmation:
            await msg.add_reaction(emoji)

        try:
            reaction = await self.bot.wait_for("reaction_add", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Took too long. Cancelled operation")
            return

        emoji = str(reaction[0].emoji)

        if not emoji == "✅":
            await ctx.send("Maybe next time. Move has been cancelled")
            return

        for person in ctx.author.voice.channel.members:
            await person.move_to(channel)

    @commands.command(brief="Command used to monitor a user", help="To be used to monitor all content the target posts within the server", usage="@user")
    @commands.has_guild_permissions(manage_channels=True)
    async def monitor(self, ctx, member:discord.Member):
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        cursor = await db.execute("SELECT * FROM MonitorTable WHERE (ID) == (?)", (member.id, ))
        row = await cursor.fetchone()
        if not row:
            await ctx.send(f"I will now be monitoring {member.name}")
            await db.execute("INSERT INTO MonitorTable (ID) VALUES (?)", (member.id, ))
        else:
            await ctx.send(f"Okay. I will no longer monitor {member.name}")
            await db.execute("DELETE FROM MonitorTable WHERE ID == (?)", (member.id, ))

        await db.commit()
        await db.close()

    # # Tasks
    # @tasks.loop(seconds=250)
    # async def saving(self):
    #     try:
    #         async with aiosqlite.connect("PCSGDB.sqlite3") as db:
    #             for user in self.users:
    #                 await db.execute("INSERT OR REPLACE INTO WarnUser (ID, WarnLevel) VALUES (?, ?)", 
    #                 (user[0], user[1]))
    #             await db.commit()
    #     except sqlite3.OperationalError:
    #         print("Database is in use.")
    #         await asyncio.sleep(120)
    #         self.saving.restart()
        

    # Functions
    async def getuser(self, m):
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        if hasattr(m, "author"):
            tag = m.author.id
        else:
            tag = m.id

        cursor = await db.execute("SELECT * FROM WarnUser WHERE (ID) == ?", (tag, ))

        row = await cursor.fetchone()

        await db.close()

        if row:
            return list(row)
        return None

    async def update_warns(self, tag, warns):
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        await db.execute("UPDATE WarnUser SET WarnLevel = ? WHERE (ID) == ?", (warns, tag))
        await db.commit()
        await db.close()

    async def is_monitored(self, member):
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        cursor = await db.execute("SELECT * FROM MonitorTable WHERE (ID) == (?)", (member.id, ))
        row = await cursor.fetchone()

        await db.close()

        if row: return True
        return False

def setup(bot):
    bot.add_cog(Moderator(bot))