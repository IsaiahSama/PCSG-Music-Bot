import discord
from discord.ext import commands, tasks
import os

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    guild = None
    chan = None

    async def async_init(self):
        await self.bot.wait_until_ready()
        self.guild = self.bot.guilds[0]

        if self.bot.user.id == 755685507907846144:
            target = 762082834235654164
        
        elif self.bot.user.id == 756347306038657085:
            target = 762150460651339806

        elif self.bot.user.id == 762167641334218762:
            target = 762171605244968990

        else: print("That's not right"); raise SystemExit

        vc = discord.utils.get(self.guild.voice_channels, id=target)
        self.chan = vc
        await self.chan.connect()
        self.reconnect.start()

    @tasks.loop(minutes=1)
    async def reconnect(self):
        if not self.guild.voice_client:
            if self.guild.voice_client.channel != self.chan:
                await self.guild.voice_client.disconnect()
                self.guild.voice_client.cleanup()
            await self.chan.connect()
            await self.playtune()

        if not self.guild.voice_client.is_playing():
            await self.playtune()


    async def playtune(self):
        vc = self.guild.voice_client
        if not vc:
            return

        if not vc.is_playing():
            
            if self.bot.user.id == 755685507907846144:
                target = "pcsgtune.mp3"
        
            elif self.bot.user.id == 756347306038657085:
                target = "pcsgtune2.mp3"

            elif self.bot.user.id == 762167641334218762:
                target = "pcsgtune3.mp3"
            
            source = discord.FFmpegOpusAudio(target)
            vc.play(source)

def setup(bot):
    bot.add_cog(Music(bot))