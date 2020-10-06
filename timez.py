import discord
from discord.ext import commands, tasks
import asyncio


class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    async def async_init(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(693608235835326464)

        await self.connect(guild)

    async def connect(self, guild):
        if self.bot.user.id == 762840423965392906:
            channel = guild.get_channel(762849851557675009)
        elif self.bot.user.id == 762840289417101352:
            channel = guild.get_channel(762849722712064031)

        await channel.connect()
        await self.prepare(guild, channel)

    async def prepare(self, guild, channel):
        cname = channel.name.split(" ")
        cname[-1] = cname[0]
        await channel.edit(name=" ".join(cname))
        await self.ticker(guild, channel, cname)       

    async def ticker(self, guild, channel, ogtime):
        while True:
            curname = channel.name.split(" ")
            curtime = int(curname[-1])
            while curtime > 0:
                await asyncio.sleep(5)
                curtime -= 1

                curname[-1] = str(curtime)
                await channel.edit(name=" ".join(curname))
                    
            await channel.edit(name=f"{ogtime} Min Study: On Break")
            await asyncio.sleep(20)
            await channel.edit(name=f"{ogtime} Min Study Time: {ogtime}")

                  

def setup(bot):
    bot.add_cog(Timer(bot))
