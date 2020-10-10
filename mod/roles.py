import discord
from discord.ext import commands
import asyncio
import random
from random import randint
import re
from time import sleep


class Rolling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Events
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        towatch = [764358056233926686, 764358088802828299, 764358029151174656, 764358062118535208]
        if not payload.message_id in towatch: return
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        emoji = payload.emoji
        emoji = str(emoji)
        msg = await channel.fetch_message(payload.message_id)
        results = re.findall(r"(.+:.+)`?", msg.content)
        
        for r in results:
            temp = r.split(":")
            emoji2 = temp[0]
            if emoji == emoji2:
                name = temp[1]
                name = name.replace("`", "")
                name = name.replace("-", " ")
                name = name.strip()
                break
            name = None
        
        if not name: print("STILL FAILED")

        role = discord.utils.get(guild.roles, name=name)
        if not role: return
        user = guild.get_member(payload.user_id)
        await user.add_roles(role)
        await user.send(f"Congrats. You now have the {role.name} role")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        towatch = [764358056233926686, 764358088802828299, 764358029151174656, 764358062118535208]

        if not payload.message_id in towatch: return
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        emoji = payload.emoji
        emoji = str(emoji)
        msg = await channel.fetch_message(payload.message_id)
        results = re.findall(r"(.+:.+)`?", msg.content)
        
        for r in results:
            temp = r.split(":")
            emoji2 = temp[0]
            if emoji == emoji2:
                name = temp[1]
                name = name.replace("`", "")
                name = name.replace("-", " ")
                name = name.strip()
                break
            name = None
        
        if not name: print("STILL FAILED")
        
        role = discord.utils.get(guild.roles, name=name)
        if not role: return
        user = guild.get_member(payload.user_id)
        await user.remove_roles(role)
        await user.send(f"Removed {role.name} role")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot: return
        role = discord.utils.get(member.guild.roles, name="Family")
        role2 = discord.utils.get(member.guild.roles, name="Newbie Learner")
        await member.add_roles(role, role2)


def setup(bot):
    bot.add_cog(Rolling(bot))