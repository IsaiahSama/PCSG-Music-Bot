import discord
from discord.ext import commands, tasks
import asyncio
import random, re

class Isaiah(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(hidden=True)
    @commands.is_owner()
    async def masssync(self, ctx):
        for channel in ctx.guild.text_channels:
            await channel.edit(sync_permissions=True)

        await ctx.send("Done and done")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def mutepls(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        overwrites = {role: discord.PermissionOverwrite(send_messages=False)}
        role2 = ctx.guild.default_role
        overwrites[role2] = discord.PermissionOverwrite(mention_everyone=False)
        roleids = [765700901377540167, 763049845841592351, 700193117281845268, 777400245398798367]
        roles = [ctx.guild.get_role(rid) for rid in roleids]
        for role in roles:
            overwrites[role] = discord.PermissionOverwrite.from_pair(discord.Permissions.all(), discord.Permissions.none())   

        for category in ctx.guild.categories:
            await category.edit(overwrites=overwrites)

        await ctx.send("Done")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def fixvoice(self, ctx):
        category = ctx.guild.get_channel(762158614839689246)
        channels = category.voice_channels
        for channel in channels:
            await channel.edit(sync_permissions=True)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def fixname(self, ctx, category_id: int):
        category = ctx.guild.get_channel(category_id)
        for channel in category.text_channels:
            emoji = channel.name[-1]
            name = channel.topic.lower()
            name = name.strip("for ")
            name = name.replace(" ", "-")

            await channel.edit(name=f"{emoji}{name}")
        await ctx.send("Fixed the channels back to normal")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def fixmoji(self, ctx, category_id: int):
        category = ctx.guild.get_channel(category_id)
        for channel in category.text_channels:
            emoji = channel.name[0]
            name = channel.name[1:]

            await channel.edit(name=f"{name}{emoji}")

        await ctx.send("Flipped Emojis and text")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def fixmistake(self, ctx, category_id: int):
        tmsg = await ctx.channel.fetch_message(764328430690369576)
        results = re.findall(r".+:.+`?", tmsg.content)
        
        cate = ctx.guild.get_channel(category_id)
        
        for result in results:
            temp = result.split(":")
            rmoji = temp[0]
            rname = temp[1]
            rname = rname.replace("`", "")
            rname = rname.strip()
            for channel in cate.text_channels:
                name = channel.name[1:]
                if name == rname: await channel.edit(name=f"{rmoji}{rname}"); break
        

    @commands.command(hidden=True)
    async def sortchan(self, ctx, category_id: int):
        await ctx.send("Beginning to sort channels now")
        cate = ctx.guild.get_channel(category_id)
        allchan = cate.voice_channels
        channames = [chan.name for chan in allchan]
        channames.sort()
        print("\n".join(channames))
        for i, v in enumerate(channames):
            channel = discord.utils.get(cate.voice_channels, name=v)
            print(f"setting {v} to position {i}")
            await channel.edit(position=i)

        await ctx.send("Sorted")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unsort(self, ctx):
        cate = ctx.channel.category
        allchan = cate.channels
        channames = [chan.name for chan in allchan]
        channames.sort()
        number = len(channames)
        for x in range(number):
            p = random.choice(allchan)
            await p.edit(position=x)

        await ctx.send("Unsorted... Cause Jazz is :shrug:")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def rolecount(self, ctx, *, name):
        role = discord.utils.get(ctx.guild.roles, name=name)
        if not role: await ctx.send("Role could not be found"); return
        users = [member for member in ctx.guild.members if role in member.roles]
        if not users: await ctx.send("No members with that role could be found"); return
        await ctx.send(f"{len(users)} members have the role {role.name}")


    @commands.command(hidden=True)
    async def roleall(self, ctx):
        await ctx.send("Beginning") 
        role = [role for role in ctx.guild.roles if role.name in ["Family", "Newbie Learner"]]
        members = [user for user in ctx.guild.members if not user.bot]

        role_channel = ctx.guild.get_channel(762068938686595152)
        intro_channel = ctx.guild.get_channel(762060265520365568)
        count = 0
        for member in members: 
            if role[0] in member.roles and role[1] in member.roles: continue
            await member.add_roles(role[0])
            await member.add_roles(role[1])
            await member.guild.get_channel(700214669003980801).send(f"Welcome to the **PCSG FAMILY** {member.mention}:heart: \nThis server is designed to help you understand how you study best and achieve every **STUDY-GOAL!!!** :partying_face: Press here: {intro_channel.mention} and introduce yourself, then press here: {role_channel.mention} to start getting your roles.")
            count += 1
            
        await ctx.send(f"Gave roles to {count} members")
        
    @commands.command(hidden=True)
    @commands.is_owner()
    async def removeall(self, ctx):
        role = [role for role in ctx.guild.roles if role.name in ["Family", "Newbie Learner"]]
        for member in ctx.guild.members: await member.remove_roles(*role)
        await ctx.send("Removed roles from everyone")


    @commands.command(hidden=True)
    @commands.is_owner()
    async def createrole(self, ctx, *, rolename):
        await ctx.guild.create_role(name=rolename)
        await ctx.send(f"Made role {rolename}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def deleterole(self, ctx, *rolename, conf=False):
        rolename = ' '.join(rolename)
        role = [x for x in ctx.guild.roles if rolename.lower() in x.name.lower()]
        if not role: await ctx.send("Cannot find a role matching that name"); return
        if len(role) > 1 and not conf:
            trole = [x.name for x in role]
            tosend = '\n'.join(trole)
            await ctx.send(f"Here is a list of roles: {tosend}")
            await ctx.send("Type the full name of the one you wish to delete, and then run the command again")
            return

        role = role[0]

        if not conf: await ctx.send(f"To confirm the deletion of this role, do p.deleterole {rolename} True"); return
        await role.delete()


    @commands.command(hidden=True)
    @commands.is_owner()
    async def aboutserv(self, ctx):
        team = discord.utils.get(ctx.guild.roles, name="Team")
        mod = discord.utils.get(ctx.guild.roles, name="Mod")
        embed = discord.Embed(
            title="About the PCSG Server",
            description=f"""
The {ctx.guild.name}, is an organisation founded by the students for the students, intialized by the pandemic of Covid-19 but with the goal to go far beyond.
The server was founded on the 28th of March, 2020 by {ctx.guild.owner.mention} as one of the greatest implementations due to Discord being a large and easy to use social platform, allowing for easy communication and organisation of information and conversations.
Moderated by the members of the PCSG Team {team.mention}, The PCSG Moderator bot {self.bot.user.mention} and The PCSG Mods {mod.mention}.
This server exists as a place where all users can feel safe and confident studying with other students doing similar subjects.""",
            color=random.randint(0, 0xffffff)
        )
        
        embed.set_thumbnail(url=ctx.guild.icon_url)

        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def aboutpcsg(self, ctx):
        embed = discord.Embed(
            title="About PCSG",
            description=f"""
The Private Caribbean Study Goals is an organsiation founded by {ctx.guild.owner.mention}, as a way of not only dealing with the pandemic of Covid-19, but also to allow students from all around the Caribbean to interact with and help each other with CSEC/CAPE Examinations.
"""
        )

        embed.set_thumbnail(url=ctx.guild.icon_url)

        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def fixroles(self, ctx):
        roles = [role for role in ctx.guild.roles if role.name.startswith(("cape", "csec"))]
        for role in roles:
            await role.edit(mentionable=True)

        await ctx.send("Finally... all subject roles are mentionable.")


    @commands.command(hidden=True)
    @commands.is_owner()
    async def create_vc(self, ctx, name):
        await ctx.send("ON IT SIR!!!")
        roles = [role for role in ctx.guild.roles if role.name.lower().startswith(f"{name.lower()} ")]
        if not roles: await ctx.send("Something ain't right here boss"); return

        category = await ctx.guild.create_category_channel(name=f"{name.upper()} Classroom")
        if not category: await ctx.send("Uhm boss... something ain't right here either."); return

        for role in roles:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                role: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True, stream=True)
            }
            x = ' '.join(role.name.split(" ")[1:])
            await category.create_voice_channel(name=f"{name.upper()} {x}", overwrites=overwrites)

        await ctx.send("Aite boss... I think we are done here")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def remove_all(self, ctx, tag:int):
        category = ctx.guild.get_channel(tag)
        for channel in category.voice_channels:
            await channel.delete()

        await category.delete()
        await ctx.send("DONE!!!")

def setup(bot):
    bot.add_cog(Isaiah(bot))
