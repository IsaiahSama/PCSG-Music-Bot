import discord
from discord.ext import commands, tasks
import asyncio
import random


class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    guild = None
    async def async_init(self):
        await self.bot.wait_until_ready()
        self.guild = self.bot.get_guild(693608235835326464)
        
        await self.connect(self.guild)

    channel = None
    async def connect(self, guild):
        # 45 minute bot
        if self.bot.user.id == 762840423965392906:
            self.channel = guild.get_channel(762849851557675009)
        # 25 minute bot
        elif self.bot.user.id == 762840289417101352:
            self.channel = guild.get_channel(762849722712064031)

        channel = self.channel
        await channel.connect()
        print("We connected")
        await self.prepare(guild, channel)

    async def prepare(self, guild, channel):
        cname = channel.name.split(" ")
        cname[-1] = cname[0]
        await channel.edit(name=" ".join(cname))
        await asyncio.sleep(300)
        await self.ticker.start()  
            

    @tasks.loop(minutes=5)
    async def ticker(self):
        channel = self.channel
        curname = channel.name.split(" ")
        ogtime = curname[0]
        curtime = int(curname[-1])
        curtime -= 5
        guild = self.bot.get_guild(693608235835326464)
        songs = ["ping!.mp3", "chill.mp3"]

        if curtime <= 0:                
            await channel.edit(name=f"{ogtime} Min Study: On Break")
            if not guild.voice_client.is_playing():
                guild.voice_client.play(discord.FFmpegOpusAudio(random.choice(songs)))
            await asyncio.sleep(300)
            await channel.edit(name=f"{ogtime} Min Study Time: {ogtime}")

        else:
            curname[-1] = str(curtime)
            await channel.edit(name=" ".join(curname))


    @tasks.loop(seconds=45)
    async def recon(self):
        if self.guild.voice_client == None:
            await self.channel.connect()

    @ticker.after_loop
    async def rentick(self):
        await self.ticker.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)

                  

def setup(bot):
    bot.add_cog(Timer(bot))
