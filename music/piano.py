import discord
from discord.ext import commands
import asyncio
import random
from random import randint
from dotenv import load_dotenv
import os
load_dotenv()

intent = discord.Intents.default()

bot = commands.Bot(command_prefix='<<<<', case_insensitive=True, intents=intent)
bot.help_command = None

bot.load_extension("music")

@bot.command()
@commands.is_owner()
async def refresh(ctx):
    bot.reload_extension("music")

@bot.event
async def on_ready():
    print(f"Piano Noises... {bot.user.name} is here")
    activity = discord.Activity(name='No', type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity, status=discord.Status.idle)


yes=os.getenv("key3")
bot.run(yes)

