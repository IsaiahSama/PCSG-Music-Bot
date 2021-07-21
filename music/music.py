import discord
from discord.errors import ClientException
from discord.ext import commands, tasks
from asyncio import sleep, TimeoutError

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    data_dict = {}

    bot_dict = {
        755685507907846144: {
            "BOT_NAME": "Lofi Bot",
            "CHANNEL_ID": 762082834235654164,
            "TRACK": "lofi.mp3"
        },
        756347306038657085: {
            "BOT_NAME": "Nature Bot",
            "CHANNEL_ID": 762150460651339806,
            "TRACK": "nature.mp3"
        },
        762167641334218762: {
            "BOT_NAME": "Piano Bot",
            "CHANNEL_ID": 762171605244968990,
            "TRACK": "piano.mp3"
        },
        820792275743014915: {
            "BOT_NAME": "Relax and vibe",
            "CHANNEL_ID": 820793494419144845,
            "TRACK": "relax.mp3"
        }
    }

    async def async_init(self):
        await self.bot.wait_until_ready()
        self.data_dict["GUILD"] = self.bot.guilds[0]
        self.data_dict["ERROR_CHANNEL"] = discord.utils.get(self.data_dict["GUILD"].text_channels, id=828638567236108308)
        self.data_dict["BOT_ID"] = self.bot.user.id

        await self.get_bot_vc()
        await self.connect_to_bot_vc()
        await self.playtune()
        self.reconnect.start()

    async def get_bot_songs_and_channel_ids(self) -> int:
        """Checks the id of the bot, sets the track it has to play, and returns the id of the channel it is to connect to.
        
        Returns channel id"""
        
        try:
            bot_dict = self.bot_dict[self.data_dict["BOT_ID"]]
            self.data_dict["TRACK"] = bot_dict["TRACK"]
        except KeyError:
            print("This bot is not one of mine.")
            raise SystemExit
            
        print("Got the song and channel id.")

        return bot_dict["CHANNEL_ID"]

    async def get_bot_vc(self):
        """ Gets the vc of the bot. Exits if it does not exist"""
        self.data_dict["VOICE_CHANNEL"] = discord.utils.get(self.data_dict["GUILD"].voice_channels, id=await self.get_bot_songs_and_channel_ids())
        if not self.data_dict["VOICE_CHANNEL"]:
            print("Could not find the voice channel for the bot to join.")
            await self.data_dict["ERROR_CHANNEL"].send("HEY BOSS, MY VOICE CHANNEL IS MISSIN'")
            raise SystemExit

        print("Got the bot's voice channel.")

    async def connect_to_bot_vc(self):
        """Function that connects to the bot vc"""
        while True:
            try:
                await self.data_dict["VOICE_CHANNEL"].connect(reconnect=True)
                break
            except TimeoutError:
                sleep(60)
                continue
            except ClientException:
                if not self.bot.voice_clients:
                    sleep(60)
                    continue
                [await v_client.disconnect() for v_client in self.bot.voice_clients]
                return False
            
    played_before = 0

    async def playtune(self):  
        """Checks if the bot is currently playing a song. If not, then try to play it """

        if not self.bot.voice_clients[0].is_playing():
            if self.played_before == 0:
                print("Bot isn't playing music. Lets begin this")
                self.played_before += 1
            else:
                print("Seems like the song is done. Time to replay it")
            try:
                self.bot.voice_clients[0].play(discord.FFmpegOpusAudio(self.data_dict["TRACK"]))
                print("Playing music")
            except ClientException as err:
                if "not connected" in str(err).lower():
                    await self.connect_to_bot_vc()
       
    @tasks.loop(minutes=1)
    async def reconnect(self):
        if (not self.bot.voice_clients) or (self.bot.voice_clients[0].channel != self.data_dict["VOICE_CHANNEL"]):
            await self.connect_to_bot_vc()

        await self.playtune()

    @commands.command()
    @commands.is_owner()
    async def get_over_here(self, ctx):
        [await vc.disconnect() for vc in self.bot.voice_clients]
        await sleep(2)
        await self.connect_to_bot_vc()
        await ctx.send("Yes")
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == "UNLOAD ZA WARUDO 493839592835907594":
            for cog in self.bot.extensions.keys():
                self.bot.unload_extension(cog)

        if message.content == "RELOAD THE LOFTY BEATS":
            if message.author.guild_permissions.move_members:
                while True:
                    try:
                        [self.bot.reload_extension(cog) for cog in self.bot.extensions.keys()]
                        await message.channel.send("Sorry. Seemed to have misplaced my music. I've found it now so feel free to come and listen")
                        break
                    except:
                        continue
            else:
                await message.channel.send("You do not have enough power to do this. Please contact a member of staff if there is an issue.")
def setup(bot):
    bot.add_cog(Music(bot))
