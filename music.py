import discord
from discord.ext import commands, tasks
import os
import asyncio



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    guild = None
    chan = None

    async def async_init(self):
        await self.bot.wait_until_ready()
        guilds = self.bot.guilds
        for g in guilds:
            if g.id == 693608235835326464:
                self.guild = g
                break

        if self.bot.user.id == 755685507907846144:
            target = 762082834235654164
        
        elif self.bot.user.id == 756347306038657085:
            target = 762150460651339806

        elif self.bot.user.id == 762167641334218762:
            target = 762171605244968990

        for chans in self.guild.voice_channels:
            if chans.id == target:
                self.chan = chans
                break
        
        await self.chan.connect()
        self.reconnect.start()

    @tasks.loop(minutes=1)
    async def reconnect(self):
        if self.guild.voice_client == None:
            await self.chan.connect()
            await self.playtune()

        if not self.guild.voice_client.is_playing():
            await self.playtune()


    async def playtune(self):
        vc = self.guild.voice_client
        if vc == None:
            return

        if not vc.is_playing() and vc is not None:
            os.chdir("C:\\Users\\zelda\\desktop")
            
            if self.bot.user.id == 755685507907846144:
                target = "pcsgtune.mp3"
        
            elif self.bot.user.id == 756347306038657085:
                target = "pcsgtune2.mp3"

            elif self.bot.user.id == 762167641334218762:
                target = "pcsgtune3.mp3"

            for link in os.listdir():
                if link.lower() == target: break
            
            source = discord.FFmpegOpusAudio(link)
            vc.play(source)



def setup(bot):
    bot.add_cog(Music(bot))