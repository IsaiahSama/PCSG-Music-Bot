import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()

intent = discord.Intents.default()

bot = commands.Bot(command_prefix='<<<', case_insensitive=True, intents=intent)
bot.help_command = None

bot.load_extension("music")

@bot.command()
@commands.is_owner()
async def refresh(ctx):
    bot.reload_extension("music")

@bot.event
async def on_ready():
    print(f"Tweet Tweet we're in")
    activity = discord.Activity(name='Nature Music for PCSG', type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity)

yes=os.getenv("key2")
bot.run(yes)

