import discord, asyncio, random
from discord.ext import commands
from random import randint


# class MyHelp(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot


#     @commands.command()
#     async def help2(self, ctx):
#         embed = discord.Embed(
#             title="Showing Help",
#             color=randint(0, 0xffffff)
#         )

#         embed.set_thumbnail(url=self.bot.user.avatar_url)
#         embed.add_field(name="p.profile", value="Shows your profile for this server")
#         embed.add_field(name="p.top", value="Shows top 5 active users")
#         embed.add_field(name="p.rank", value="Shows your rank for this server")
#         embed.add_field(name="p.serverinfo", value="Shows basic server information")
#         embed.add_field(name="p.portal channelName", inline=False, value="Opens a 'portal' to the channel whose name you specify. Emojis not needed")
#         embed.add_field(name="p.scheduleset", value="Allows you to set your schedule")
#         embed.add_field(name="p.myschedule", value="Shows your schedule for the day")
#         embed.add_field(name="p.clrschedule day", inline=False, value="Clears your schedule for that day")
#         embed.add_field(name="p.rules", value="Shows the rules", )
#         embed.add_field(name="p.takenote (do p.note for an example on how to use the command.)", inline=False, value="Used to take a notes for yourself and peerss")
#         embed.add_field(name="p.getnote [tag, title or id]", inline=False, value="Gets a note either by tag, id or by title.")
#         embed.add_field(name="p.delnote id", value="Deletes a note by ID. Only works for the owner of the note, or by moderators")
#         embed.add_field(name="p.wiki tosearch", value="Searches the wide wikipedia for your requests")
#         embed.add_field(name="p.fact", value="Gives you a random fact.")
#         embed.add_field(name="p.find @mention", value="To be used on someone who is in one of the server's voice channels. Reveals their location")

#         await ctx.send(embed=embed)

#     @commands.command()
#     async def modhelp(self, ctx):
#         roles = [x for x in ctx.guild.roles if x.name.lower() in ["admin", "mod", "team"]]

#         if ctx.author.top_role in roles:
#             embed = discord.Embed(
#                 title="Showing Help",
#                 color=randint(0, 0xffffff)
#             )

#             embed.add_field(name="p.ban @mention reason", value="Bans a user", inline=False)
#             embed.add_field(name="p.kick @mention reason", value="Kicks a user", inline=False)
#             embed.add_field(name="p.timeout @mention duration reason", value="Mutes a user", inline=False)
#             embed.add_field(name="p.mute @mention reason", value="Mutes a user", inline=False)
#             embed.add_field(name="p.unmute @mention", value="Unmutes a user", inline=False)
#             embed.add_field(name="p.warn @mention reason", value="Increases a user's warning level by 1", inline=False)
#             embed.add_field(name="p.resetwarn @mention", value="Resets a user's warning level", inline=False)
#             embed.add_field(name="p.warnreset", value="Resets warning level for everyone in the server", inline=False)
#             embed.add_field(name="p.warnstate @mention", value="Shows how many warns a user has", inline=False)
#             embed.add_field(name="p.warned", value="Shows top 10 people with highest warns", inline=False)
#             embed.add_field(name="p.slow duration", value="Sets a slowmode on channel for x seconds", inline=False)

#             await ctx.send(embed=embed)
#             return
        
#         await ctx.send("YOU ARE NOT A MOD")


class MyHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        if command.usage:
            return f'{self.clean_prefix}{command.name} {command.usage}'
        return f'{self.clean_prefix}{command.name}'

    def command_not_found(self, string):
        raise commands.CommandNotFound

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Showing help for {command.qualified_name}",
            color=randint(0, 0xffffff)
        )
        if command.usage:
            embed.add_field(name="Usage:", value=f"```{self.clean_prefix}{command.name} {command.usage}```", inline=False)
        else:
            embed.add_field(name="Usage:", value=f"```{self.clean_prefix}{command.name}```", inline=False)

        embed.add_field(name="Brief:", value=f"```{command.brief}```", inline=False)
        embed.add_field(name="Help:", value=f"```{command.help}```", inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=f"```{command.aliases}```")
        if command.cog:
            embed.add_field(name="Cog:", value=f"```{command.cog.qualified_name}```")
        
        embed.set_footer(text=self.get_opening_note())
    
        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"Showing information on {cog.qualified_name}",
            description=cog.description,
            color=randint(0, 0xffffff)
        )

        to_loop = await self.filter_commands(cog.get_commands())
        if not to_loop: await self.get_destination().send("This Cog has no commands."); return
        for command in to_loop:
            embed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"```{command.brief}```")
        embed.set_footer(text=self.get_opening_note())

        
        await self.get_destination().send(embed=embed)


    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="Showing help for you",
            color=randint(0, 0xffffff)
        )

        to_loop = [k for k in mapping.keys() if k]

        to_loop = list(set(to_loop))
        for cog in to_loop:
            if cog.description:
                embed.add_field(name=cog.qualified_name, value=f"```{cog.description}```")
                embed.set_footer(text=f"PS: These are Case Sensitive\n{self.get_opening_note()}")

        await self.get_destination().send(embed=embed)

    
class MyHelp(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(MyHelp(bot))