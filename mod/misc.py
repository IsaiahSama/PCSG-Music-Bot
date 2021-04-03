import discord
from discord.ext import commands, tasks
import asyncio
import random
import wikipedia as wp



class Misc(commands.Cog):
    """For the use of commands that don't have their own category."""
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    async def async_init(self):
        await self.bot.wait_until_ready()
        self.chancount.start()
        self.studycount.start()

    @tasks.loop(minutes=5)
    async def chancount(self):
        guild = self.bot.get_guild(693608235835326464)
        famcount = guild.get_channel(764418047246729227)
        members = [mem for mem in guild.members if not mem.bot]
        temp = famcount.name.split(":")
        name = temp[0]
        num = len(members)
        new_name = f"{name}: {num}"
        if famcount.name == new_name: return
        await famcount.edit(name=new_name)
        

    @tasks.loop(minutes=5)
    async def studycount(self):
        guild = self.bot.get_guild(693608235835326464)
        studycount = guild.get_channel(764427421876748298)
        total = 0
        for vc in guild.voice_channels:
            temp = [user for user in vc.members if not user.bot]
            total += len(temp)

        temp = studycount.name.split(":")
        name = temp[0]
        if studycount.name == f"{name}: {total}": return
        await studycount.edit(name=f"{name}: {total}")

    @commands.command(brief="Used to see information on the server", help="Reveals some basic information on the PCSG server")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        guilded = discord.Embed(
            title=f"Showing server info for {ctx.guild.name}",
            color=random.randint(0, 0xffffff)
        )        
        humans = [member for member in ctx.guild.members if not member.bot]
        bots = [member for member in ctx.guild.members if member.bot]

        guilded.set_thumbnail(url=guild.icon_url)
        guilded.add_field(name="Guild Name", value=f"{guild.name}")
        guilded.add_field(name="Date Created",
                          value=f"{guild.created_at.strftime('%d/%m/%y')}")
        guilded.add_field(name="Time Created", value=f"{guild.created_at.hour}:{guild.created_at.minute}:{guild.created_at.second} UTC")
        guilded.add_field(name="Guild Region", value=f"{guild.region}")
        guilded.add_field(name="Guild Owner", value=f"{guild.owner}")
        guilded.add_field(name="Number of humans", value=f"{len(humans)}")        
        guilded.add_field(name="Number of bots", value=f"{len(bots)}")        
        guilded.add_field(name="Number of Text Channels", value=f"{len(ctx.guild.text_channels)}")
        guilded.add_field(name="Number of Voice Channels", value=f"{len(ctx.guild.voice_channels)}")
        guilded.add_field(name="Number of roles", value=f"{len(ctx.guild.roles)}")

        await ctx.send(embed=guilded)

    @commands.command(brief="Shows the rules for the server", help="Shows the rules for the server")
    async def rules(self, ctx):
        embed = discord.Embed(
            title="Rules for this server",
            color=random.randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name=f"Rule 1:", value=f"It is mandatory to go to the Roles category and select the roles which concern you", inline=False)
        embed.add_field(name=f"Rule 2:", value=f"Be respectful to everyone. If you encounter any issues, inform the mods before taking other actions", inline=False)
        embed.add_field(name=f"Rule 3:", value=f"Keep channel discussions to their respective channels", inline=False)
        embed.add_field(name=f"Rule 4:", value=f"In order to take part in classes. Zoom and a Google account and required as classes will be hosted on those 2 platforms", inline=False)
        embed.add_field(name=f"Rule 5:", value=f"Follow the rules", inline=False)
        embed.set_footer(text="Check with p.rules")

        await ctx.send(embed=embed)

    @commands.command(brief="Shows Rules for Classes", help="Shows the rules to be followed for classes")
    async def classrules(self, ctx):
        embed= discord.Embed(
            title="Showing Rules For Online Classes",
            color=random.randint(0, 0xffffff)
        )
        #RULES FOR PCSG ZOOM CLASSES: 

        # 1. Students must be respectful to Student-Hosts and fellow students.

        # 2. Students MUST have an appropriate name in order to enter the class (full name). This will be recorded in the roll book with your contact number.

        # 3. Profanity (inappropriate language, behaviour or images) and unnecessary noise is forbidden in class. 

        # 4. If students have any questions, they must first raise their hand and then the Student-Host will unmute the student who wishes to speak.

        # 5. READ THE RULES.

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Rule 1:", value="Students must be respectful to Student-Hosts and fellow students", inline=False)
        embed.add_field(name="Rule 2:", value="Students MUST have their real name in order to be accepted into the class. This will be recorded in the roll book along with your contact number.")
        embed.add_field(name="Rule 3:", value="Profanity of any kind and unnecessary noise is forbidden in class", inline=False)
        embed.add_field(name="Rule 4:", value="If students have any questions, they will be expected to raise their hand to alert the Student-Host who will then unmute the student who wishes to speak.")
        embed.add_field(name="Rule 5:", value="Students will be expected to give their full focus to the class at hand. If you wish to not do so, ensure that you do not affect the other students in any way or form.", inline=False)
        embed.add_field(name="Rule 6:", value="If for any reason, a student has to leave their device for any period of time, they will be expected to alert the Student-Host in an appropiate manner")
        embed.add_field(name="Rule 7:", value="Failure to comply to the above rules will result in a warning. Several offenses will result in immediate dismissal from the class, and potentially being banned.", inline=False)
        embed.add_field(name="Rule 8:", value="Follow the rules and good studying to all of you.")
        embed.set_footer(text="Can be viewed at anytime with p.classrules")

        await ctx.send(embed=embed)

    def sync_func(self, results, x):
        for result in results:
            try:
                data = wp.summary(result, sentences=x)
                return data
            except wp.exceptions.PageError: continue

        return None

    
    @commands.command(aliases=["wikipedia"], brief="Instantly search the wikipedia for whatever you want", help="Searches the wikipedia for what you asked. Wikipedia is a bit... difficult at times however.", usage="something")
    async def wiki(self, ctx, *, tosearch):
        results = wp.search(tosearch)
        if results: await ctx.send(f"Here are results for {tosearch}.\n {results}")
        async with ctx.channel.typing():
            data = await self.bot.loop.run_in_executor(None, self.sync_func, results, 5)       

            if not data: await ctx.send("Could not find that result"); return
            await ctx.send(f"Here you go {ctx.author.mention}:\n{data}")

    @commands.command(brief="Gives you a random fact.", help="Tells you a random potentially interesting fact, yeeted right from Wikipedia")
    async def fact(self, ctx):
        fact = wp.random()
        async with ctx.channel.typing():
            result = wp.search(fact)
            data = await self.bot.loop.run_in_executor(None, self.sync_func, result, 1) 
            await ctx.send(f"Your fact is: {data}")   

    @commands.command(brief="Shows you which voice channel someone is in.", help="Use this to find someone who you know is in a voice channel, but not sure as to which one they are in", usage="@user")
    async def find(self, ctx, member: discord.Member):
        if not member.voice: await ctx.send(f"{member.name} is not in a voice channel")
        else: await ctx.send(f"{member.name} is in {member.voice.channel.name}")

    @commands.command(brief="See who's available when you are so you can study with them", help="Looking for a study buddy of sorts? Use this command to see who's online and doing your same subjects and available when you are")
    async def matchfind(self, ctx):
        prof_channel = ctx.guild.get_channel(762068938686595152)
        sub_channel_1 = ctx.guild.get_channel(755875615587958814)
        sub_channel_2 = ctx.guild.get_channel(718473529452003329)
        caperole = [x for x in ctx.guild.roles if "cape " in x.name]
        csecrole = [x for x in ctx.guild.roles if "csec " in x.name]
        profrole = [x for x in ctx.guild.roles if x.name in ["csec", "cape"]]

        user_profic = [proficiency for proficiency in profrole if proficiency in ctx.author.roles]
        if not user_profic: await ctx.send(f"You have not selected your role for csec/cape. Select them from here {prof_channel.mention}"); return
        if user_profic[0].name == "csec":
            user_subjects = [subject.name for subject in csecrole if subject in ctx.author.roles]
        else:
            user_subjects = [subject.name for subject in caperole if subject in ctx.author.roles]

        if not user_subjects: await ctx.send(f"You don't have any subject roles. Get them from {sub_channel_1.mention} or {sub_channel_2.mention}"); return
        
        await ctx.send("Searching for people with subjects similar to yours that are currently not offline")
        members = []
        for member in ctx.guild.members:
            if member == ctx.author: continue
            if member.status == discord.Status.offline: continue
            profic = [proficiency for proficiency in profrole if proficiency in member.roles and proficiency in ctx.author.roles]

            if not profic: continue
            if profic[0].name == "csec":
                subjects = [subject.name for subject in csecrole if subject in member.roles and subject in ctx.author.roles]
            else:
                subjects = [subject.name for subject in caperole if subject in member.roles and subject in ctx.author.roles]

            if not subjects: continue
            members.append(member)

        if len(members) == 0: await ctx.send("Could not find anyone matching your criteria"); return
        await ctx.send(f"Found {len(members)} members")
        embed = discord.Embed(
            title=f"Showing members that meet {ctx.author.name}'s criteria",
            color=random.randint(0, 0xffffff)
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        

        for member in members[:25]:
            embed.add_field(name="Available:", value=member.mention)

        await ctx.send(embed=embed)  


def setup(bot):
    bot.add_cog(Misc(bot))
