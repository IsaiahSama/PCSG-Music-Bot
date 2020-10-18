import discord
from discord.ext import commands
import asyncio
import random
from random import randint
from dotenv import load_dotenv
import os
load_dotenv()

intent = discord.Intents.default()

bot = commands.Bot(command_prefix='>>>', case_insensitive=True, intents=intent)
bot.help_command = None

bot.load_extension("timez")

@bot.command()
@commands.is_owner()
async def refresh(ctx):
    bot.reload_extension("timez")

@bot.event
async def on_ready():
    print(f"Timer for 45 mins, just for you")
    activity = discord.Activity(name='45 minute timer', type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity)

yes=os.getenv("key5")
bot.run(yes)

