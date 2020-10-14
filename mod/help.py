import discord, asyncio
from discord.ext import commands
from random import randint


class MyHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="Showing Help",
            color=randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="p.profile", value="Shows your profile for this server")
        embed.add_field(name="p.top", value="Shows top 5 active users")
        embed.add_field(name="p.rank", value="Shows your rank for this server")
        embed.add_field(name="p.serverinfo", value="Shows basic server information")
        embed.add_field(name="p.portal channelName", inline=False, value="Opens a 'portal' to the channel whose name you specify. Emojis not needed")
        embed.add_field(name="p.scheduleset", value="Allows you to set your schedule")
        embed.add_field(name="p.myschedule", value="Shows your schedule for the day")
        embed.add_field(name="p.clrschedule day", inline=False, value="Clears your schedule for that day")
        embed.add_field(name="p.rules", value="Shows the rules", )
        embed.add_field(name="p.takenote (do p.note for an example on how to use the command.)", inline=False, value="Used to take a notes for yourself and peerss")
        embed.add_field(name="p.getnote [tag, title or id]", inline=False, value="Gets a note either by tag, id or by title.")
        embed.add_field(name="p.delnote id", value="Deletes a note by ID. Only works for the owner of the note, or by moderators")
        embed.add_field(name="p.wiki tosearch", value="Searches the wide wikipedia for your requests")
        embed.add_field(name="p.fact", value="Gives you a random fact.")
        embed.add_field(name="p.find @mention", value="To be used on someone who is in one of the server's voice channels. Reveals their location")

        await ctx.send(embed=embed)

    @commands.command()
    async def modhelp(self, ctx):
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


def setup(bot):
    bot.add_cog(MyHelp(bot))