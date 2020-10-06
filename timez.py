import discord
from discord.ext import commands, tasks
import asyncio

class TimerKing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    channel = None
    guild = None

    async def async_init(self):
        await self.bot.wait_until_ready()
        self.guild = self.bot.get_guild(693608235835326464)
        if self.bot.user.id == 762840423965392906:
            target = 762849851557675009

        # Timer 25
        elif self.bot.user.id == 762840289417101352:
            target = 762849722712064031

        self.channel = discord.utils.get(self.guild.voice_channels, id=target)
        await self.channel.connect()
        await self.prepare()
        await self.ticker.start()
        await self.reconnect.start()


    async def prepare():
        channel = self.channel
        if self.bot.user.id == 762840289417101352:
            timer = 25
        elif self.bot.user.id == 762840423965392906:
            timer = 45

        cname = channel.name.split(" ")
        cnum = cname[-1]
        if type(cnum) is not int: 
            await channel.edit(name=f"{channel.name} Time: {timer}")

        await self.ticker.start()       

    @tasks.loop(minutes=1)
    async def ticker(self):
        if self.bot.user.id == 762840289417101352:
            timer = 25
        elif self.bot.user.id == 762840423965392906:
            timer = 45

        channel = self.channel
        time = channel.name.split(" ")[-1]
        time -= 1

        if time == 0:
            await channel.edit(name=f"{channel.name} Break Time")
            await asyncio.sleep(300)
            await channel.edit(name=f"{channel.name} Time: {timer}")


    @tasks.loop(minutes=1)
    async def reconnect(self):
        if self.guild.voice_client == None:
            await self.channel.connect()



def setup(bot):
    bot.add_cog(TimerKing(bot))
