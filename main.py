import discord
from discord.ext import commands
import asyncio
import random
from random import randint
from dotenv import load_dotenv
import os
load_dotenv()

bot = commands.Bot(command_prefix='<<', case_insensitive=True)
bot.help_command = None

bot.load_extension("roles")
bot.load_extension("music")

@bot.command()
@commands.is_owner()
async def refresh(ctx):
    bot.reload_extension("roles")

yes=os.getenv("key")
bot.run(yes)

