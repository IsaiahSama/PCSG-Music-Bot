import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from random import randint
import aiosqlite

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="p.", case_insensitive=True, intents=intents)
bot.help_command = None

bot.load_extension("roles")
bot.load_extension("levels")
bot.load_extension("sfw")
bot.load_extension("portals")
bot.load_extension("misc")
bot.load_extension("isaiah")
bot.load_extension("schedule")
bot.load_extension("help")
bot.load_extension("notes")

@bot.event
async def on_ready():
    print(f"Right...")
    activity = discord.Activity(name='for p.help', type=discord.ActivityType.listening)
    await bot.change_presence(activity=activity)    

@bot.command()
@commands.is_owner()
async def rc(ctx, *, cog=None):
    if not cog:
        bot.reload_extension("roles")
        bot.reload_extension("levels")
        bot.reload_extension("sfw")
        bot.reload_extension("portals")
        bot.reload_extension("misc")
        bot.reload_extension("isaiah")
        bot.reload_extension("schedule")
        bot.reload_extension("help")
        bot.reload_extension("notes")

        await ctx.send("Reloaded Cogs")

    else:
        try:
            bot.reload_extension(cog)    
            await ctx.send(f"{cog} has been reloaded")
        except discord.ext.commands.ExtensionNotLoaded:
            await ctx.send("Extension could not be found")

@bot.command()
@commands.is_owner()
async def uc(ctx, *, cog):
    try:
        bot.unload_extension(cog)    
        await ctx.send(f"{cog} has been unloaded")
    except discord.ext.commands.ExtensionNotLoaded:
        await ctx.send("Extension could not be found")


yes = os.getenv("keymod")
bot.run(yes)
