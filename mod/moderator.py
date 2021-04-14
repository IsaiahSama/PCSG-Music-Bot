import discord, time, asyncio, aiosqlite, os, json, sqlite3, time
from discord import utils
from discord.ext.commands.cooldowns import BucketType
from mydicts import *
from discord.ext import commands, tasks
from random import randint

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

            await db.commit()

        await self.setup()

    users = []

    async def setup(self):
        guild = self.bot.get_guild(guild_id)
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
        await log("Warn", f"{member.name} was warned:", str(ctx.author), reason)
        
    @commands.command(brief="This resets the warns that a person has back to 0", help="This sets the warns of a user back to 0.", usage="@user")
    @commands.has_permissions(administrator=True)
    async def resetwarn(self, ctx, member: discord.Member):
        user = await self.getuser(member)
        user['WARNLEVEL'] = 0
        await ctx.send(f"Reset warns on {member.name} to 0")
        await log("Resetwarn", f"{str(member)} had their warns reset", str(ctx.author), reason="None")

    @commands.command(brief="Mutes a user for x seconds", help="Mutes a user for the specified number of seconds", usage="@user duration_in_seconds reason")
    @commands.has_permissions(administrator=True)
    async def timeout(self, ctx, member: discord.Member, time, *, reason):
        role = discord.utils.get(ctx.guild.roles, id=all_roles["MUTED"])
        await member.add_roles(role)
        await ctx.send(f"{member.mention} has been timed out for {time} minutes for {reason} by {ctx.author.name}")
        time *= 60

        await asyncio.sleep(time)

        await ctx.send(f"{member.mention}. Your timeout has come to an end. Refrain from having to be timed out again")
        await member.remove_roles(role)
        await log("Timeout", f"{str(member)} was timed-out for {time} seconds", str(ctx.author), reason)

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
        await log("Warn Reset", "Everyone had their crimes cleared", str(ctx.author), reason="Unknown")

    @commands.command(brief="Deletes x amount of messages", help="Used to bulk delete messages")
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, amount:int):
        await ctx.channel.purge(limit=amount)

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
            role = discord.utils.get(message.guild.roles, id=all_roles["MUTED"])
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

        pending_member_role = discord.utils.get(member.guild.roles, id=all_roles["PENDING_MEMBER"])

        await member.add_roles(pending_member_role)

        human_count = sum(not human.bot for human in member.guild.members)

        if human_count % 100 == 0:
            await member.guild.get_channel(channels["WELCOME_CHANNEL"]).send(f"CONGRATULATIONS TO {member.mention} FOR BEING THE {human_count}th HUMAN TO JOIN THE PCSG FAMILY!!!")
            
        await member.guild.get_channel(channels["WELCOME_CHANNEL"]).send(
f"""Welcome {member.mention} to the <:PCSGLETTERSWITHOUTBACKGROUND:828392100729978900> Family! <a:catholdheart:830938992081371157> You're the {sum(not user.bot for user in member.guild.members)}th Family Member <:holdheart:830939097518178375>
Thank You for joining The Study-Goals' E-School <a:movingstar:830939250513674311>

Please follow The Registration Process <:blueexclamation:830938893204455454>:
<a:greentick:830939074712961035> Press here: {member.guild.get_channel(channels["REP_FLAG"]).mention}  to select your country.
<a:greentick:830939074712961035> Press here: {member.guild.get_channel(channels["PERSONALIZE_CHANNEL"]).mention} to personalize The E-School to your criteria.
<a:blacktick:830938918262013952>Press here: {member.guild.get_channel(channels["VERIFY"]).mention} to personalize the server to accomodate your CXC subjects and UNLOCK the FULL E-School
***DONE***  <a:party:830939382944628766>

We look forward to learning with you, Newbie E-Schooler! <a:catmovinghead:830939036033875999> 
Feel free to invite your family & friends: <a:animalscheering:830938963761299456> https://youtu.be/9B1-1Wgi9lw 
""")
        await member.guild.get_channel(channels["WELCOME_CHANNEL"]).send("https://cdn.discordapp.com/attachments/813888001775370320/831305455237988402/WELCOME_TO_STUDY_GOALS_E-SCHOOL_4.gif")

        await self.handle_new_user(member)

    async def handle_new_user(self, member):
        channel = member.guild.get_channel(channels["PERSONALIZE_CHANNEL"])
        await channel.send(f"Hello there {member.mention}. I just need to ask you a few questions before you're all ready to go. Firstly, what is your name?")
        
        await self.handle_name(member)
        group_size_message = await channel.send(f"\nNice to meet you {member.display_name}. Now, what size group do you prefer to study in?\n\n🕑2 People / duo\n\n🕒3 People / trio\n\n🕓4 People / quartet\n\n🕔5 people / quintet\n Press all the emojis below that apply to you, then press ✅ to confirm")
        group_size_roles = await self.handle_group_size(member, group_size_message)

        proficiency_message = await channel.send(f"\n\nSo {member.mention}, what's your proficiency?\n📘 CSEC or 📖 CAPE?\nPress all the emojis below that apply to you, then press ✅ to confirm")
        proficiency_roles = await self.handle_proficiency(member, proficiency_message)
        
        await member.add_roles(*group_size_roles, *proficiency_roles)
        prof_channel = discord.utils.get(member.guild.text_channels, id=channels[proficiency_roles[0].name.upper()])
        msg = f"\n\nAlright {member.mention} head over to {prof_channel.mention} to select your subjects"
        if len(proficiency_roles) > 1:
            prof_channel2 = discord.utils.get(member.guild.text_channels, id=channels[proficiency_roles[1].name.upper()])
            msg += f"and {prof_channel2}"
        await channel.send(msg)

    async def handle_name(self, member):
        def check(m):
            return m.author == member

        response = await self.bot.wait_for("message", check=check)
        name = response.content 

        await member.edit(nick=name)

    async def handle_group_size(self, member, message):
        def check(reaction, user):
            return user == member and str(reaction.emoji) in list(group_roles.keys())
        
        for key in list(group_roles.keys()):
            await message.add_reaction(key)
        
        roles = []
        while True:
            group_size_raw_emoji = await self.bot.wait_for("reaction_add", check=check)
            if str(group_size_raw_emoji[0].emoji) == "✅":
                if roles:
                    break
            roles.append(utils.get(member.guild.roles, id=group_roles_ids[group_roles[str(group_size_raw_emoji[0].emoji)]]))
        return roles

    async def handle_proficiency(self, member, message):
        pro_dict = {"📘": "CSEC", "📖": "CAPE", "✅":"Confirm"}

        def check(reaction, user):
            return user == member and str(reaction.emoji) in pro_dict

        for key in list(pro_dict.keys()):
            await message.add_reaction(key)

        roles = []
        while True:
            raw_proficiency = await self.bot.wait_for("reaction_add", check=check)
            emoji = str(raw_proficiency[0].emoji)
            if emoji == "✅":
                if roles:
                    break
            roles.append(utils.get(member.guild.roles, id=all_roles[pro_dict[emoji]]))

        return roles

    @commands.command(brief="A command used to go through the verification process", help="This is a command that allows an unverified user to take part in the verification process.")
    async def verify(self, ctx):
        pending_role = ctx.guild.get_role(all_roles["PENDING_MEMBER"])
        if pending_role not in ctx.author.roles:
            await ctx.send("You are already Verified")
            return 
        
        await self.handle_new_user(ctx.author)

    @commands.command(brief="A command used to find all members that have yet to verify", help="Prompts all unverified users to take part in the verification process")
    @commands.cooldown(1, 3600, BucketType.guild)
    async def retrack(self, ctx):
        pending_role = ctx.guild.get_role(all_roles["PENDING_MEMBER"])
        unverified = [member for member in ctx.guild.members if pending_role in member.roles]
        if not unverified:
            await ctx.send("Everyone is verified :D")
            return 
        
        veri_channel = ctx.guild.get_channel(channels["PERSONALIZE_CHANNEL"])

        for stranger in unverified:
            await veri_channel.send(f"Hey, {stranger.mention}. You still aren't verified. Aren't you feeling lonely out there? Simply type `p.verify` to begin the verification process and come join the rest of the school")

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



def setup(bot):
    bot.add_cog(Moderator(bot))