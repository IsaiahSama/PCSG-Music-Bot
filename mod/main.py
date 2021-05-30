import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from random import randint
import aiosqlite

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["P.", "p."], case_insensitive=True, intents=intents)
# bot.help_command = None

bot.load_extension("levels")
bot.load_extension("moderator")
bot.load_extension("general")
bot.load_extension("schedule")
bot.load_extension("help")
bot.load_extension("notes")
bot.load_extension("isaiah")
bot.load_extension("eventhandler")

@bot.event
async def on_ready():
    print(f"Right...")
    activity = discord.Activity(name='p.help', type=discord.ActivityType.listening)
    await bot.change_presence(activity=activity, status=discord.Status.dnd)    

@bot.command(hidden=True)
@commands.is_owner()
async def rc(ctx, *, cog=None):
    if not cog:
        for cog in bot.extensions.keys():
            bot.reload_extension(cog)
        await ctx.send("Reloaded all cogs")    

    else:
        try:
            bot.reload_extension(cog)    
            await ctx.send(f"{cog} has been reloaded")
        except discord.ext.commands.ExtensionNotLoaded:
            await ctx.send("Extension could not be found")

@bot.command(hidden=True)
@commands.is_owner()
async def uc(ctx, *, cog):
    try:
        bot.unload_extension(cog)    
        await ctx.send(f"{cog} has been unloaded")
    except discord.ext.commands.ExtensionNotLoaded:
        await ctx.send("Extension could not be found")


yes = os.getenv("keymod")
bot.run(yes)
