import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="^>", case_insensitive=True, intents=intents)
bot.help_command = None

bot.load_extension("roles")

@bot.command()
async def rc(ctx):
    bot.reload_extension("roles")
    await ctx.send("Cogs Have been reloaded")


yes = os.getenv("keymod")
bot.run(yes)
