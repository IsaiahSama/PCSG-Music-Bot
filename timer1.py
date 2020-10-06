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
    print(f"Timer for 25 mins just for me")
    activity = discord.Activity(name='Timing students for 25', type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity)

yes=os.getenv("key4")
bot.run(yes)

