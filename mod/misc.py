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

    @commands.command()
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

    @commands.command()
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

    
    @commands.command(aliases=["wiki"])
    async def wikipedia(self, ctx, *, tosearch):
        results = wp.search(tosearch)
        if results: await ctx.send(f"Here are results for {tosearch}.\n {results}")
        async with ctx.channel.typing():
            data = await self.bot.loop.run_in_executor(None, self.sync_func, results, 5)       

            if not data: await ctx.send("Could not find that result"); return
            await ctx.send(f"Here you go {ctx.author.mention}:\n{data}")

    @commands.command()
    async def fact(self, ctx):
        fact = wp.random()
        async with ctx.channel.typing():
            result = wp.search(fact)
            data = await self.bot.loop.run_in_executor(None, self.sync_func, result, 1) 
            await ctx.send(f"Your fact is: {data}")   

    @commands.command()
    async def find(self, ctx, member: discord.Member):
        if not member.voice: await ctx.send(f"{member.name} is not in a voice channel")
        else: await ctx.send(f"{member.name} is in {member.voice.channel.name}")  


def setup(bot):
    bot.add_cog(Misc(bot))
