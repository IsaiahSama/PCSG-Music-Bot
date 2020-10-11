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
    daydict = {}
    cxcdict = {}
    
    ids = [754573710974779443, 754561589163589743, 764787663776645140, 764790530181300244]
    roleids = [764795950979088384, 764795982713061397, 764795923858587648, 764795955689291817, 764795892904755200, 764796084316667945]

    async def async_init(self):
        await self.bot.wait_until_ready() 
        await self.thing()

    async def thing(self):
        guild = self.bot.get_guild(693608235835326464)
        await self.getroles(guild)
        print("Done")

    async def getroles(self, guild):
        dicts = [self.capedict, self.csecdict, self.daydict, self.cxcdict]
        for i, v in enumerate(self.ids):
            cate = guild.get_channel(v)
            channels = cate.text_channels
            for chan in channels:
                emoji = chan.name[0]
                name = chan.name[1:]
                t = dicts[i]
                t[emoji] = name

    @commands.command()
    @commands.is_owner()
    async def roleselect(self, ctx, mode):
        await ctx.send(f"React with the appropiate emoji for your role")
        tosend = []
        ab = []
        if mode == "cape": check = self.capedict.items()
        elif mode == "csec": check = self.csecdict.items()
        elif mode == "days": check = self.daydict.items()
        elif mode == "cxc": check = self.cxcdict.items()
        else: print("Bad mode"); return
        for k, v in check: 
            tdict = {}
            tdict[k] = v
            ab.append(tdict)

        if len(ab) > 20:
            a = ab[:20]
            b = ab[21:]
        else: a, b = ab, None
        for d in a:
            for k, v in d.items():
                tmsg = f"{k}: `{v}`"
                tosend.append(tmsg)
            
        tosend = '\n'.join(tosend)
        msg = await ctx.send(tosend)

        for d in a:
            for v in d.keys():
                await msg.add_reaction(v)

        if not b: return
        
        tosend = []
        for d in b:
            for k, v in d.items():
                tmsg = f"{k}: `{v}`"
                tosend.append(tmsg)
        tosend = '\n'.join(tosend)
        msg = await ctx.send(tosend)
        for d in b:
            for v in d.keys():
                await msg.add_reaction(v)

    # Events
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.roleids:
        
            guild = self.bot.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
            emoji = payload.emoji
            emoji = str(emoji)
        
            results = re.findall(r"(.+:.+)`?", msg.content)
        
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

            role = discord.utils.get(guild.roles, name=name)
            if not role: print("can't find role"); return
            user = guild.get_member(payload.user_id)
            await user.add_roles(role)
            await user.send(f"Congrats. You now have the {role.name} role")
        else:
            print("Nope")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        print("I also activated")
        if not payload.message_id in self.roleids: return
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