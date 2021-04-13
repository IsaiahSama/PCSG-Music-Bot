from discord.errors import HTTPException
from mydicts import *
import discord 
from discord.ext import commands 
from random import randint
from os import path

class EventHandling(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        bot.loop.create_task(self.async_init())

    async def async_init(self):
        await self.bot.wait_until_ready()
        print("Event Handler is ready")

    @commands.Cog.listener()
    async def on_member_ban(self, member):
        bann = await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        ban = bann[0]

        embed = discord.Embed(
            title="I see... Now you're banned",
            description=f"{str(ban.target)} has been banned by {str(ban.user)}",
            color=randint(0, 0xffffff)
        )

        embed.add_field(name="Reason", value=ban.reason)
        embed.set_footer(text=f"Target ID {ban.target.id}. Banner ID {ban.user.id}")

        await member.guild.get_channel(channels["JOIN_LEAVES"]).send(embed=embed)

    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="Leaving",
            description=f"It would seem as though {str(member)} has left the server",
            color=randint(0, 0xffffff)
        )

        entry = await member.guild.audit_logs(limit=1).flatten()
        entry = entry[0]
        if entry.action is discord.AuditLogAction.kick:
            embed.add_field(name=":o , It was a kick", value=f"{str(entry.target)} was kicked by {str(entry.user)} for {entry.reason}")
        
        await member.guild.get_channel(channels["JOIN_LEAVES"]).send(embed=embed)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.embeds: return
        embed = discord.Embed(
            description=f"{str(before.author)} made an edit to a message in {after.channel.name}",
            title="A message has been edited.",
            color=randint(0, 0xffffff)
        )

        embed.add_field(name="Before", value=before.content or "Unknown")
        embed.add_field(name="After", value=after.content or "Unknown", inline=False)
        embed.add_field(name="Jump URL", value=after.jump_url)
        embed.set_footer(text=f"User ID: {before.author.id}")

        await before.guild.get_channel(channels["MESSAGE_LOGS"]).send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        changed, embed = await self.was_changed(before, after)
        if not embed: return

        if changed == "nickname":
            channel = before.guild.get_channel(channels["NAME_CHANGES"])
        elif changed == "roles":
            channel = before.guild.get_channel(channels["ROLE_CHANGES"])
        else: return

        embed.set_footer(text=f"User ID: {before.id}")

        await channel.send(embed=embed)
        

    async def was_changed(self, before, after):
        if not before.nick == after.nick:
            if not after.nick: after.nick = after.name
            embed = discord.Embed(
                title="Wait... so they want to have a nickname?",
                description=f"{str(before)} would like to be known as {after.nick}",
                color=randint(0, 0xffffff)
            )
            return "nickname", embed

        if not before.roles == after.roles:
            value = await before.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten()
            value = value[0]
            try:
                initial = value.before.roles[0].name
            except IndexError:
                initial = "Received the role"
            try:
                final = value.after.roles[0].name
            except IndexError:
                final = "was removed"
            
            embed = discord.Embed(
                title=f"Role updates for {before.name}/{before.nick}",
                description=f"{str(value.user)} changed {value.target}'s roles. {initial} {final}",
                color=randint(0, 0xffffff)
            )

            return "roles", embed

        return None, None

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        embed = discord.Embed(
            title=f"{message.author} had a deleted message in {message.channel.name}",
            description=message.content,
            color=randint(0, 0xffffff)
        )
        channel = message.guild.get_channel(channels["MESSAGE_LOGS"])
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messagelist):
        embed = discord.Embed(
            title="Bulk Deletion",
            description=f"{len(messagelist)} messages were bulk deleted.",
            color=randint(0, 0xffffff)
        )

        for msg in messagelist[:24]:
            embed.add_field(name=f"Deleted from {msg.channel.name}", value=f"{msg.content[:550]} ...")

        await messagelist[0].guild.get_channel(channels["BULK_DELETES"]).send(embed=embed)
    


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error_channel = ctx.guild.get_channel(channels["ERROR_ROOM"])

        if isinstance(error, commands.CommandNotFound):
            all_cogs = self.bot.cogs
            msg = ctx.message.content.lower().split(".")[1]
            
            potential = []
            for v in all_cogs.values():
                mycommands = v.get_commands()
                if not mycommands: continue
                yes = [name.name for name in mycommands if msg in name.name.lower()]
                if yes:
                    for i in yes: potential.append(i)

            if potential:
                await ctx.send(f"I don't know that command, maybe one of these: {', '.join(potential)}")
            else:
                await ctx.send("Uhm... Try p.help for a list of my commands because I don't know that one")
            return

        await ctx.send(error)
        print(error)
        await error_channel.send(error)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id in list(raw_react_channel_ids.keys()):
            await self.handle_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id in list(raw_react_channel_ids.keys()):
            await self.handle_reaction(payload)

    async def handle_reaction(self, payload):
        guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
        member = payload.member or discord.utils.get(guild.members, id=payload.user_id)
        bot_channel = guild.get_channel(channels["BOT_ROOM"])
        # So this will get a bit confusing... even for me, so let's take this slow
        # raw_react_channel_ids will link the id of the channel to a name
        # This name when put in of reactions, will link it to it's respective dictionaries of reactions
        # This innermost dict will match the stringified emoji to role name, and then assign. Simple :D
        role = discord.utils.get(guild.roles, name=reactions[raw_react_channel_ids[payload.channel_id]][str(payload.emoji)])


        if payload.event_type == "REACTION_ADD":
            if role.name == "Pending Member":
                await member.remove_roles(role)
                family_role = member.guild.get_role(roles["FAMILY"])
                newbie_role = member.guild.get_role(roles["NEWBIE"])
                await member.add_roles(family_role, newbie_role)
                msg = "Excellent, you're now an official member :D"
            else:
                await member.add_roles(role)
                msg = f"There you go, {role.name} is now yours."
        else:
            if role.name == "Pending Member":
                return
            await member.remove_roles(role)
            msg = f"I have removed {role.name} from you."
    
        try:    
            await member.send(msg)
        except HTTPException:
            await bot_channel.send(f"{member.mention}, I can't directly message you. To avoid this in the future, go into the server's privacy settings and enable direct messages. Anyway, your message:\n{msg}")       


def setup(bot):
    bot.add_cog(EventHandling(bot))