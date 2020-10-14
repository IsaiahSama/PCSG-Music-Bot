import discord
from discord.ext import commands, tasks
import asyncio
import random, re, os


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
        value = self.bot.user.name.split(" ")[0].replace("min", "")
        await channel.edit(name=f"({value})Study Time: {value}")
        await asyncio.sleep(300)
        self.ticker.start()  
            

    @tasks.loop(minutes=5)
    async def ticker(self):
        guild = self.bot.get_guild(693608235835326464)
        channel = self.channel
        value = self.bot.user.name.split(" ")[0].replace("min", "")
        current_time = re.findall(r": ([0-9]+)", channel.name)
        if current_time: current_time = int(current_time[0])
        else: 
            print("Something went wrong")
            await channel.edit(name=f"({value})Study Time: {value}")
            return

        current_time -= 5

        songs = ["ping!.mp3", "chill.mp3"]

        if current_time <= 0:                
            await channel.edit(name=f"On Break")
            if not guild.voice_client.is_playing():
                guild.voice_client.play(discord.FFmpegOpusAudio(random.choice(songs)))
            await asyncio.sleep(300)
            await channel.edit(name=f"({value})Study Time: {value}")

        else:
            await channel.edit(name=f"({value})Study Time: {current_time}")



    @tasks.loop(seconds=45)
    async def recon(self):
        if self.guild.voice_client == None:
            await self.channel.connect()

    @ticker.after_loop
    async def rentick(self):
        self.ticker.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)    

def setup(bot):
    bot.add_cog(Timer(bot))
