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

@bot.event
async def on_ready():
    print(f"Right...")
    activity = discord.Activity(name='for p.help', type=discord.ActivityType.watching)
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

        await ctx.send("Reloaded Cogs")

    else:
        try:
            bot.reload_extension(cog)    
            await ctx.send(f"{cog} has been reloaded")
        except discord.ext.commands.ExtensionNotLoaded:
            await ctx.send("Extension could not be found")

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Showing Help",
        color=randint(0, 0xffffff)
    )

    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.add_field(name="p.profile", value="Shows your profile for this server", inline=False)
    embed.add_field(name="p.top", value="Shows top 5 active users", inline=False)
    embed.add_field(name="p.rank", value="Shows your rank for this server", inline=False)
    embed.add_field(name="p.serverinfo", value="Shows basic server information", inline=False)
    embed.add_field(name="p.portal channelName", value="Opens a 'portal' to the channel whose name you specify. Emojis not needed", inline=False)
    embed.add_field(name="p.scheduleset", value="Allows you to set your schedule", inline=False)
    embed.add_field(name="p.myschedule", value="Shows your schedule for the day", inline=False)
    embed.add_field(name="p.clrschedule day", value="Shows your schedule for the day", inline=False)
    embed.add_field(name="p.rules", value="Shows the rules", inline=False)
    embed.add_field(name="p.wiki tosearch", value="Searches the wide wikipedia for your requests", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def modhelp(ctx):
    roles = [x for x in ctx.guild.roles if x.name.lower() in ["admin", "mod", "team"]]

    if ctx.author.top_role in roles:
        embed = discord.Embed(
            title="Showing Help",
            color=randint(0, 0xffffff)
        )

        embed.add_field(name="p.ban @mention reason", value="Bans a user", inline=False)
        embed.add_field(name="p.kick @mention reason", value="Kicks a user", inline=False)
        embed.add_field(name="p.timeout @mention duration reason", value="Mutes a user", inline=False)
        embed.add_field(name="p.mute @mention reason", value="Mutes a user", inline=False)
        embed.add_field(name="p.unmute @mention", value="Unmutes a user", inline=False)
        embed.add_field(name="p.warn @mention reason", value="Increases a user's warning level by 1", inline=False)
        embed.add_field(name="p.resetwarn @mention", value="Resets a user's warning level", inline=False)
        embed.add_field(name="p.warnreset", value="Resets warning level for everyone in the server", inline=False)
        embed.add_field(name="p.warnstate @mention", value="Shows how many warns a user has", inline=False)
        embed.add_field(name="p.warned", value="Shows top 10 people with highest warns", inline=False)
        embed.add_field(name="p.slow duration", value="Sets a slowmode on channel for x seconds", inline=False)

        await ctx.send(embed=embed)
        return
    
    await ctx.send("YOU ARE NOT A MOD")
    


yes = os.getenv("keymod")
bot.run(yes)
