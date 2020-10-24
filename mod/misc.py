import discord
from discord.ext import commands, tasks
import asyncio
import random
import wikipedia as wp

class Misc(commands.Cog):
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
        embed.add_field(name=f"1)", value=f"It is mandatory to go to the Roles category and select the roles which concern you", inline=False)
        embed.add_field(name=f"2)", value=f"Be respectful to everyone. If you encounter any issues, inform the mods before taking other actions", inline=False)
        embed.add_field(name=f"3)", value=f"Keep channel discussions to their respective channels", inline=False)
        embed.add_field(name=f"4)", value=f"In order to take part in classes. Zoom and a Google account and required as classes will be hosted on those 2 platforms", inline=False)
        embed.add_field(name=f"5)", value=f"Follow the rules", inline=False)

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
    async def seeschedule(self, ctx):
        dayrole = [x for x in ctx.guild.roles if x.name.endswith("day")]
        caperole = [x for x in ctx.guild.roles if "cape " in x.name]
        csecrole = [x for x in ctx.guild.roles if "csec " in x.name]
        profrole = [x for x in ctx.guild.roles if x.name in ["csec", "cape"]]

        user_profic = [proficiency for proficiency in profrole if proficiency in ctx.author.roles]
        if not user_profic: await ctx.send("You have not selected your role for csec/cape"); return
        user_days = [day.name for day in dayrole if day in ctx.author.roles]
        if not user_days: await ctx.send("You have not selected your role for which days you are available"); return
        if user_profic[0].name == "csec":
            user_subjects = [subject.name for subject in csecrole if subject in ctx.author.roles]
        else:
            user_subjects = [subject.name for subject in caperole if subject in ctx.author.roles]

        if not user_subjects: await ctx.send("You don't have any subject roles"); return
        
        await ctx.send("Searching for people doing your subjects whose available days matches yours")
        members = []
        for member in ctx.guild.members:
            if member == ctx.author: continue
            if member.status == discord.Status.offline: continue
            days = [day.name for day in dayrole if day in member.roles and day in ctx.author.roles]

            if not days: continue
            profic = [proficiency for proficiency in profrole if proficiency in member.roles and proficiency in ctx.author.roles]

            if not profic: continue
            if profic[0].name == "csec":
                subjects = [subject.name for subject in csecrole if subject in member.roles and subject in ctx.author.roles]
            else:
                subjects = [subject.name for subject in caperole if subject in member.roles and subject in ctx.author.roles]

            if not subjects: continue
            members.append(member)

        if len(members) == 0: await ctx.send("Could not find anyone matching your criteria"); return
        await ctx.send(len(members))
        embed = discord.Embed(
            title=f"Showing members that meet {ctx.author.name}'s criteria",
            color=random.randint(0, 0xffffff)
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        for member in members[:25]:
            embed.add_field(name="Available:", value=member)

        await ctx.send(embed=embed)  


def setup(bot):
    bot.add_cog(Misc(bot))
