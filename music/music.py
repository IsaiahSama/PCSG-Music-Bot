import discord
from discord.errors import ClientException
from discord.ext import commands, tasks

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    data_dict = {}

    async def async_init(self):
        await self.bot.wait_until_ready()
        self.data_dict["GUILD"] = self.bot.guilds[0]
        self.data_dict["ERROR_CHANNEL"] = discord.utils.get(self.data_dict["GUILD"].text_channels, id=828638567236108308)
        self.data_dict["BOT_ID"] = self.bot.user.id
        
        if self.data_dict["BOT_ID"] == 755685507907846144:
            target = 762082834235654164
            self.data_dict["TRACK"] = "lofi.mp3"
        
        elif self.data_dict["BOT_ID"] == 756347306038657085:
            target = 762150460651339806
            self.data_dict["TRACK"] = "nature.mp3"

        elif self.data_dict["BOT_ID"] == 762167641334218762:
            target = 762171605244968990
            self.data_dict["TRACK"] = "piano.mp3"

        elif self.data_dict["BOT_ID"] == 820792275743014915:
            target = 820793494419144845
            self.data_dict["TRACK"] = "relax.mp3"
            
        else: print("That's not right"); raise SystemExit

        self.data_dict["VOICE_CHANNEL"] = discord.utils.get(self.data_dict["GUILD"].voice_channels, id=target)
        if not self.data_dict["VOICE_CHANNEL"]:
            print("Something went wrong.")
            await self.data_dict["ERROR_CHANNEL"].send("HEY BOSS, MY VOICE CHANNEL IS MISSIN'")
            raise SystemExit
        
        try:
            self.data_dict["VC_OBJECT"] = await self.data_dict["VOICE_CHANNEL"].connect()
        except:
            print("Already connected")
        self.reconnect.start()

    @tasks.loop(minutes=1)
    async def reconnect(self):
        if not self.data_dict["VC_OBJECT"].is_connected():
            try:
                self.data_dict["VC_OBJECT"] = await self.data_dict["VOICE_CHANNEL"].connect()
            except ClientException:
                pass

        if self.data_dict["VC_OBJECT"].channel != self.data_dict["VOICE_CHANNEL"]:
            await self.data_dict["VC_OBJECT"].disconnect()
            self.data_dict["VC_OBJECT"] = await self.data_dict["VOICE_CHANNEL"].connect()

        if not self.data_dict["VC_OBJECT"].is_playing():
            try:
                await self.playtune()
            except Exception as err:
                print(f"An error occurred... Look at this {err}")
                await self.data_dict["ERROR_CHANNEL"].send(f"An error occurred... Look at this:\n{err}")

    async def playtune(self):                    
        self.data_dict["VC_OBJECT"].play(discord.FFmpegOpusAudio(self.data_dict["TRACK"]))

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