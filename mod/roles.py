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
        bot.loop.create_task(self.async_init())

    capedict = {}
    csecdict = {}
    dictcapesec = {}

    async def async_init(self):
        await self.bot.wait_until_ready() 
        await self.thing()

    async def thing(self):
        guild = self.bot.get_guild(693608235835326464)
        await self.getcapes(guild)
        await self.getcsecs(guild)
        await self.getpart2(guild)
        print("Done")

    async def getcapes(self, guild):
        cate = guild.get_channel(754573710974779443)
        channels = cate.text_channels
        for chan in channels:
            emoji = chan.name[0]
            name = chan.name[1:]
            self.capedict[emoji] = name

    async def getcsecs(self, guild):
        cate = guild.get_channel(754561589163589743)
        channels = cate.text_channels
        for chan in channels:
            emoji = chan.name[0]
            name = chan.name[1:]
            self.csecdict[emoji] = name

    async def getpart2(self, guild):
        chan = guild.get_channel(762068938686595152)
        msg = await chan.fetch_message(764689348444291132)
        print(msg)
        results = re.findall(r"(.+:.+)`?", msg.content)
        for item in results:
            temp = item.split(":")
            emoji = temp[0]
            name = item[1]
            print(emoji, name)
            self.dictcapesec[emoji] = name


    # Events
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        towatch = [764358056233926686, 764358088802828299, 764358029151174656, 764358062118535208, 764661637364973588]
        if not payload.message_id in towatch: return
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        emoji = payload.emoji
        print(type(payload.emoji))
        emoji = str(emoji)
        msg = await channel.fetch_message(payload.message_id)
        print(msg)
        results = re.findall(r"(.+:.+)`?", msg.content)
        print(results)
        
        for r in results:
            temp = r.split(":")
            emoji2 = temp[0]
            print(emoji2)
            if emoji == emoji2:
                name = temp[1]
                name = name.replace("`", "")
                name = name.replace("-", " ")
                name = name.strip()
                break
            name = None
        
        if not name: print("STILL FAILED")

        print(name)

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
        print(results)
        
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