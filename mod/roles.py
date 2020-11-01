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
    group = {}
    
    ids = [754573710974779443, 754561589163589743, 764787663776645140, 764790530181300244, 765008580143087617]
    roleids = [765345502907596840, 765345536244318220, 765345755505360937, 765345790616141874, 764795892904755200, 764796084316667945, 765013168846012458]

    async def async_init(self):
        await self.bot.wait_until_ready() 
        await self.thing()

    async def thing(self):
        guild = self.bot.get_guild(693608235835326464)
        await self.getroles(guild)
        print("Done")

    async def getroles(self, guild):
        dicts = [self.capedict, self.csecdict, self.daydict, self.cxcdict, self.group]
        for i, v in enumerate(self.ids):
            cate = guild.get_channel(v)
            channels = cate.text_channels
            for chan in channels:
                emoji = chan.name[0]
                name = chan.name[1:]
                t = dicts[i]
                t[emoji] = name

    @commands.command(hidden=True)
    @commands.is_owner()
    async def roleselect(self, ctx, mode):
        await ctx.send(f"React with the appropiate emoji for your role")
        tosend = []
        ab = []
        if mode == "cape": check = self.capedict.items()
        elif mode == "csec": check = self.csecdict.items()
        elif mode == "days": check = self.daydict.items()
        elif mode == "cxc": check = self.cxcdict.items()
        elif mode == "group": check = self.group.items()
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

    async def check(self, ctx, mid):
        msg = await ctx.fetch_message(mid)
        reactions = msg.reactions
        for reaction in reactions:
            users = await reaction.users().flatten()
            for user in users:
                if type(user) == discord.User:
                    await reaction.remove(user)

    @commands.command(hidden=True)
    async def reroll(self, ctx, mid:int):
        msg = await ctx.fetch_message(mid)
        await self.check(ctx, mid)
        reactions = msg.reactions
        for reaction in reactions:
            users = await reaction.users().flatten()
            results = re.findall(r"(.+:.+)`?", msg.content)
            emoji = str(reaction.emoji)
        
            for r in results:
                temp = r.split(":")
                emoji2 = temp[0]
                if emoji == emoji2:
                    name = temp[1]
                    name = name.replace("`", "").replace("-", " ").strip()
                    break

            role = discord.utils.get(ctx.guild.roles, name=name)
            for user in users:
                if user.bot: continue
                if role in user.roles: continue
                await user.add_roles(role)
                await user.send(f"Sorry for being late, Here's your {role.name} role")

        msg2 = await ctx.send("Done... Probably")
        await asyncio.sleep(5)
        await ctx.message.delete()
        await msg2.delete()



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
                if emoji == emoji2:
                    name = temp[1]
                    name = name.replace("`", "").replace("-", " ").strip()
                    break
                name = None
            
            if not name: print("STILL FAILED")
        
            role = discord.utils.get(guild.roles, name=name)
            if not role: print(f"can't find role for {name}"); return
            user = guild.get_member(payload.user_id)
            await user.add_roles(role)
            await user.send(f"Congrats. You now have the {role.name} role")


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
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
                name = name.replace("`", "").replace("-", " ").strip()
                break
            name = None
        
        if not name: print("STILL FAILED")

        role = discord.utils.get(guild.roles, name=name)
        if not role: return
        user = guild.get_member(payload.user_id)
        if role not in user.roles: return
        await user.remove_roles(role)
        await user.send(f"Removed {role.name} role")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot: return
        role = discord.utils.get(member.guild.roles, name="Family")
        role2 = discord.utils.get(member.guild.roles, name="Newbie Learner")
        await member.add_roles(role, role2)
        await member.guild.get_channel(700214669003980801).send(f"Welcome to the **PCSG FAMILY** {member.mention}:heart: \nThis server is designed to help you understand how you study best and achieve every **STUDY-GOAL!!!** :partying_face:")


    # @commands.command()
    # async def test(self, member):
    #     file = discord.File("logo.png")

    #     await member.send(file=file)

def setup(bot):
    bot.add_cog(Rolling(bot))