import discord
from discord.ext import commands, tasks
import asyncio
import random

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


    
def setup(bot):
    bot.add_cog(Misc(bot))
