import discord
from discord.ext import commands
import asyncio

class Portaling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(brief="This is used to go to any text channel within the server", help="This command creates a 'portal' of sorts that you can press to go to any text channel within the PCSG server.", usage="name_of_channel")
    async def portal(self, ctx, *, channame):
        channels = ctx.guild.text_channels
        channel = [chan.mention for chan in channels if channame.lower() in chan.name.lower()]
        if not channel: await ctx.send(f"Channel with {channame} could not be found"); return
        
        await ctx.send(''.join(channel[:49]))


    @commands.command(hidden=True)
    @commands.is_owner()
    async def countall(self, ctx):
        allcount = 0
        for category in ctx.guild.categories:
            counter = 0
            for _ in category.channels: counter += 1; allcount += 1

            await ctx.send(f"{category.name}: {counter} channels")

        await ctx.send(f"{allcount} channels in all")

    
def setup(bot):
    bot.add_cog(Portaling(bot))
