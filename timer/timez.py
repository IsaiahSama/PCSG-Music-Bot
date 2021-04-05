import discord
from discord import utils
from discord.ext import commands, tasks
import asyncio
import random, re, os


class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    data_dict = {}
    async def async_init(self):
        await self.bot.wait_until_ready()
        self.data_dict["GUILD"] = self.bot.get_guild(693608235835326464)
        self.data_dict["ERROR_CHANNEL"] = discord.utils.get(self.data_dict["GUILD"].text_channels, id=755875929208782928)
        self.data_dict["BOT_ID"] = self.bot.user.id
        # 45 minute bot
        if self.data_dict["BOT_ID"] == 762840423965392906:
            target = 762849851557675009
        # 25 minute bot
        elif self.data_dict["BOT_ID"] == 762840289417101352:
            target = 762849722712064031
        else:
            self.data_dict["ERROR_CHANNEL"].send(f"An {self.bot.user.name} is using MEEEE")
            raise SystemExit
        
        self.data_dict["CHANNEL"] = utils.get(self.data_dict["GUILD"].voice_channels, id=target)
        if not self.data_dict["CHANNEL"]:
            print("Can't find my designated voice channel")
            return
        
        self.data_dict["VC_OBJECT"] = await self.data_dict["CHANNEL"].connect()
        print("We connected")
        await self.prepare(self.data_dict["CHANNEL"])
        self.recon.start()


    async def prepare(self, channel):
        value = self.bot.user.name.split(" ")[0].replace("min", "")
        await channel.edit(name=f"({value})Study Time: {value}")
        await asyncio.sleep(300)
        self.ticker.start()  
            

    @tasks.loop(minutes=5)
    async def ticker(self):
        channel = self.data_dict["CHANNEL"]
        value = self.bot.user.name.split(" ")[0].replace("min", "")
        current_time = re.findall(r": ([0-9]+)", channel.name)
        if current_time: current_time = int(current_time[0])
        else: 
            print("Something went wrong")
            await channel.edit(name=f"({value})Study Time: {value}")
            return

        current_time -= 5

        songs = ["Ping!.mp3", "chill.mp3"]

        if current_time <= 0:                
            await channel.edit(name=f"On Break")
            if not self.data_dict["VC_OBJECT"].is_playing():
                try:
                    self.data_dict["VC_OBJECT"].play(discord.FFmpegOpusAudio(random.choice(songs)))
                except Exception as err:
                    print(f"An error occurred... Look at this {err}")
                    await self.data_dict["ERROR_CHANNEL"].send(f"An error occurred... Look at this:\n{err}")
                    return
            await asyncio.sleep(298)
            await channel.edit(name=f"({value})Study Time: {value}")

        else:
            await channel.edit(name=f"({value})Study Time: {current_time}")

    @tasks.loop(seconds=60)
    async def recon(self):
        if not self.data_dict["VC_OBJECT"].is_connected():
            self.data_dict["VC_OBJECT"] = await self.data_dict["CHANNEL"].connect()
        
        if self.data_dict["VC_OBJECT"].channel != self.data_dict["CHANNEL"]:
            await self.data_dict["VC_OBJECT"].disconnect(force=True)
            self.data_dict["VC_OBJECT"] = await self.data_dict["CHANNEL"].connect()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)    

def setup(bot):
    bot.add_cog(Timer(bot))
