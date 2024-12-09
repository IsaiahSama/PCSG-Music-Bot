import discord
from discord import utils
from discord.ext import commands
from discord.ext.commands import Bot
import random, re
from re import compile

from discord.permissions import PermissionOverwrite
from mydicts import *
import traceback

class Isaiah(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot:Bot):
        self.bot = bot
        
    @commands.command(hidden=True)
    @commands.is_owner()
    async def masssync(self, ctx):
        for channel in ctx.guild.text_channels:
            await channel.edit(sync_permissions=True)

        await ctx.send("Done and done")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def mutepls2(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name="E-Muted")
        overwrites = {role: discord.PermissionOverwrite(send_messages=False)}
        role2 = ctx.guild.default_role
        overwrites[role2] = discord.PermissionOverwrite(mention_everyone=False)
        roleids = [765700901377540167, 763049845841592351, 700193117281845268, 777400245398798367]
        roles = [ctx.guild.get_role(rid) for rid in roleids]
        for role in roles:
            overwrites[role] = discord.PermissionOverwrite.from_pair(discord.Permissions.all(), discord.Permissions.none())   

        for channel in ctx.guild.channels:
            await channel.edit(overwrites=overwrites)

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
    @commands.is_owner()
    async def sortchanv2(self, ctx, category_id: int, kind, has_emoji=False):
        await ctx.send("Beginning to sort channels now")
        category = ctx.guild.get_channel(category_id)
        if kind == "voice":
            channels = category.voice_channels
        elif kind == "text":
            channels = category.text_channels
        elif kind == "all":
            channels = category.channels
        else:
            await ctx.send("Kind should be `voice`, `text` or `all`")
            return

        restoration_dict = None
        if has_emoji:
            og_names = [channel.name for channel in channels]
            names = []
            for channel in channels:
                emoji = channel.name[0]
                name = channel.name[1:]
                await channel.edit(name=f"{name}{emoji}")
                names.append(channel.name)

            restoration_dict = dict(zip(names, og_names))
        else:
            names = [channel.name for channel in channels]

        names.sort()
        print("\n".join(names))
        for i, v in enumerate(names):
            channel = discord.utils.get(channels, name=v)
            print(f"setting {v} to position {i}")
            await channel.edit(position=i)

        await ctx.send("Sorted")

        if restoration_dict:
            await ctx.send("Restoring emojis to their position")
            for k, v in restoration_dict.items():
                channel = discord.utils.get(channels, name=k)
                await channel.edit(name=v)

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
    @commands.is_owner()
    async def removeall(self, ctx):
        role = [role for role in ctx.guild.roles if role.name in [762190942316134400, 755633133600112651]]
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

    @commands.command(hidden=True)
    @commands.is_owner()
    async def new_perms(self, ctx, word, cid:int):
        if word == "csec":
            teacher = discord.utils.get(ctx.guild.roles, id=762189597059842058)
        elif word == "cape":
            teacher = discord.utils.get(ctx.guild.roles, id=796519532628803584)
        else:
            print("No no no... NO!")
            return
        match = re.compile(rf"({word}.+)")
        category = ctx.guild.get_channel(cid)
        for channel in category.text_channels:
            name = match.search(channel.name).group(1)
            name = name.replace("-", " ")
            role = discord.utils.get(ctx.guild.roles, name=name)
            if not role:
                print(f"Failed to get role for {channel.name}")
                continue

            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                teacher: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
            }

            await channel.edit(overwrites=overwrites)
            print(f"Changed overwrites for {channel.name}")

    @commands.command()
    @commands.is_owner()
    async def lets_not_mess_up_please(self, ctx):
        role = ctx.guild.get_role(all_roles["PENDING_MEMBER"])
        await ctx.send(f"Got {role.name}. Moving into stage 2")

        for channel in ctx.guild.channels:
            og_overwrites = channel.overwrites
            og_overwrites[role] = discord.PermissionOverwrite(view_channel=False)
            await channel.edit(overwrites=og_overwrites)

        await ctx.send("We got it... we all goodx")


    @commands.command()
    @commands.is_owner()
    async def lets_test_this_first(self, ctx):
        role = ctx.guild.get_role(all_roles["PENDING_MEMBER"])
        await ctx.send(f"Got {role.name}. Moving into stage 2")
        og_overwrites = ctx.channel.overwrites
        og_overwrites[role] = discord.PermissionOverwrite(view_channel=False)
        await ctx.channel.edit(overwrites=og_overwrites)
        await ctx.send("Done... Check the results senor")

    @commands.command()
    @commands.is_owner()
    async def send_message(self, ctx, *, msg):
        await ctx.message.delete()
        await ctx.send(msg)

    @commands.command()
    @commands.is_owner()
    async def send_veri_msg(self, ctx, *, msg):
        await ctx.message.delete()
        message = await ctx.send(msg)
    
        await message.add_reaction("✅")

    @commands.command()
    async def add_reaction(self, ctx, mid:int, reaction):
        message = await ctx.channel.fetch_message(mid)
        await message.add_reaction(reaction)
        await ctx.message.delete()

    @commands.command()
    @commands.is_owner()
    async def set_perms_2(self, ctx, cid:int):
        from re import compile
        compiled = compile(r"[A-Za-z]+")
        category = ctx.guild.get_channel(cid)
        for channel in category.channels:
            letters_only = " ".join(compiled.findall(channel.name))
            role = discord.utils.get(ctx.guild.roles, name=letters_only)
            if not role:
                await ctx.send(f"Could not find role for {channel.name}. Letters found were {letters_only}")            
                continue
            
            overwrites = channel.overwrites

            overwrites[ctx.guild.default_role] = PermissionOverwrite(connect=False, view_channel=False, mention_everyone=False)
            overwrites[role] = PermissionOverwrite(connect=True, view_channel=True)
            if "cape" in letters_only:
                x = ctx.guild.get_role(796519532628803584)
            else:
                x = ctx.guild.get_role(762189597059842058)

            overwrites[x] = PermissionOverwrite(connect=True, view_channel=True)

            await channel.edit(overwrites=overwrites)

        await ctx.send("Done")

    @commands.command()
    @commands.is_owner()
    async def clear_perms(self, ctx, cid:int):
        category = ctx.guild.get_channel(cid)
        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        for channel in category.channels:
            await channel.edit(overwrites=overwrites)

        await ctx.send("DONE BOSS")

    @commands.command()
    @commands.is_owner()
    async def clear_topics(self, ctx, cid:int):
        category = ctx.guild.get_channel(cid)
        for channel in category.channels:
            await channel.edit(topic=None)

        await ctx.send("Set all topics to None")

    @commands.command()
    @commands.is_owner()
    async def change_topics(self, ctx, cid:int):
        category = ctx.guild.get_channel(cid)
        from re import compile
        reg = compile(r"[A-Za-z]+")
        for channel in category.channels:
            letters = ' '.join(reg.findall(channel.name))
            topic = letters + " class now"
            await channel.edit(topic=topic.upper())

    @commands.command()
    @commands.is_owner()
    async def fix_channel_names(self, ctx, cid:int):
        category = ctx.guild.get_channel(cid)
        from re import compile
        exp = compile(r"[A-Za-z]+")
        for channel in category.channels:
            letters = ' '.join(exp.findall(channel.name))
            new_name = f"{letters} streamroom"
            await channel.edit(name=new_name)

    @commands.command()
    @commands.is_owner()
    async def find_strangers(self, ctx):
        family = ctx.guild.get_role(all_roles["FAMILY"])
        humans = [member for member in ctx.guild.members if not member.bot]
        strangers = [human for human in humans if not family in human.roles]

        welcome_channel = ctx.guild.get_channel(channels["WELCOME_CHANNEL"])

        newbie = ctx.guild.get_role(all_roles["NEWBIE"])

        i = 0

        for stranger in strangers:
            await stranger.add_roles(family, newbie)
            await welcome_channel.send(f"Officially welcoming {stranger.mention} to the PCSG Family. Thanks for joining, and we look forward to studying with you.\n\n You are the {(len(humans) - len(strangers)) + i} family member")
            await welcome_channel.send("https://media.discordapp.net/attachments/813888001775370320/831305455237988402/WELCOME_TO_STUDY_GOALS_E-SCHOOL_4.gif")
            i += 1

        await ctx.send(f"Found {len(strangers)} strangers and gave them their roles")

    @commands.command()
    @commands.is_owner()
    async def sp(self, ctx, cid:int, term:str):
        category = ctx.guild.get_channel(cid)
        if not category:
            await ctx.send("This category does not exist?")
            return
        proficiency = ctx.guild.get_role(all_roles[term.upper()])
        mo = compile(rf".*({term}.+)")
        for channel in category.channels:
            role_name = mo.search(channel.name)[1].replace("-", " ").replace(" streamroom", "")
            role = utils.get(ctx.guild.roles, name=role_name)
            if not role:
                print(f"Could not get role for {channel.name}")
                continue
            overwrites = channel.overwrites
            if not overwrites:
                await ctx.send("This channel does not have any overwrites. Making them now")
                overwrites = {}
            overwrites[proficiency] = PermissionOverwrite(view_channel=False)
            overwrites[role] = PermissionOverwrite(view_channel=True)
            await channel.edit(overwrites=overwrites)

        await ctx.send("Sync complete")
       
    @commands.command()
    @commands.is_owner()
    async def transition(self, ctx):
        family = ctx.guild.get_role(all_roles["FAMILY"])

        unverified = [member for member in ctx.guild.members if family not in member.roles and not member.bot]
        for person in unverified:
            try:
                await person.edit(roles=[])
            except:
                await ctx.send(f"Could not edit {person.display_name}'s roles")

        await ctx.send("DONE")

    @commands.command()
    @commands.is_owner()
    async def alert(self, ctx):
        family = ctx.guild.get_role(all_roles["FAMILY"])
        members = [member for member in ctx.guild.members if family not in member.roles and not member.bot]
        channel = ctx.guild.get_channel(834839533978779718)

        msg = "Sorry for the inconvenience. In an attempt to make the server easier to use, I ended up making it harder :sweat_smile: . The process has been removed entirely, so now all you need to do is state your name, and then select the roles that you want. Note, Selecting these roles ARE optional, but they greatly assist in making sure that you can get help when you need it."

        for member in members:
            try:
                await member.send(msg)
            except:
                await channel.send(f"Hey {member.mention}. {msg}")
        
        await ctx.send("Informed everyone about the change")
                

    @commands.command()
    @commands.is_owner()
    async def sleepy_boy(self, ctx):
        stage_5 = ctx.guild.get_role(all_roles["STAGE_5_YEAR"])

        for channel in ctx.guild.channels:
            overwrites = channel.overwrites
            overwrites[stage_5] = PermissionOverwrite(view_channel=False, connect=False)
            await channel.edit(overwrites=overwrites)

        await ctx.send("Finished I am sleepy boy")

    @commands.command()
    @commands.is_owner()
    async def edit_message(self, ctx, mid:int, *, new_message):
        message = await ctx.channel.fetch_message(mid)
        await message.edit(content=new_message)

        await ctx.message.delete()

    @commands.command()
    @commands.is_owner()
    async def normies_cant_see(self, ctx):
        ids = [785986612717944832, 761092169757884416, 700556455274610698, 700211825102553099, 764790530181300244, 762033167683026976, 825901516060885073, 754573710974779443, 827652047087468625]
        categories = [ctx.guild.get_channel(id1) for id1 in ids]

        for category in categories:
            for channel in category.channels:
                overwrites = channel.overwrites
                overwrites[ctx.guild.default_role] = PermissionOverwrite(mention_everyone=False, view_channel=False)
                await channel.edit(overwrites=overwrites)
            
        await ctx.send("Everything is now private")
        
    the_dicts = {
    # Countries
    700174264782815232: {700230631228964915},
    # Groups
    762068609278410752: {833324711516700703},
    # Proficieny
    762068938686595152: {833328249622495233},
    # Cape Sub Select
    718473529452003329: {765345755505360937, 765345790616141874},
    # Csec Sub Select
    755875615587958814: {765345502907596840, 765345536244318220},
    # Specialties
    839580152131485696: {840074038688350248}
    }

    @commands.command()
    @commands.is_owner()
    async def track_reactions(self, ctx):
        for channel_id, message_ids in self.the_dicts.items():
          for message_id in message_ids:
            # Fetches the message
            m = await ctx.guild.get_channel(channel_id).fetch_message(message_id)
            # Index my register channels dicts to get my name for the channel
            channel_name = register_channels[channel_id]
            for reaction in m.reactions:
              # Index my reactions dict to get the name of the role
              # Same line, get the role via discord.utils
              try:
                role = discord.utils.get(ctx.guild.roles, name=reactions[channel_name][str(reaction.emoji)])
              except:
                continue
              # Get a list of all users
              users = await reaction.users().flatten()
              # Gets only people currently in the server
              members = [user for user in users if isinstance(user, discord.Member)]
              targets = [member for member in members if not role in member.roles]
              # Adds the role to the Target and tries to dm them. 
              for target in targets:
                await target.add_roles(role)
                try:
                    await target.send(f"Sorry for being late. I have just given you the {role.name} role")
                except Exception:
                    pass
              if targets:
                await ctx.send(f"Gave the {role.name} role to {len(targets)} members.")
              else:
                await ctx.send(f"We covered everyone for the {role.name} role.")
                
    @commands.command()
    @commands.is_owner()
    async def f(self, ctx):
        nicknamed = [member for member in ctx.guild.members if member.nick]
        targets = [target for target in nicknamed if target.nick.startswith("my name is")]
        [target.edit(nick=target.nick.split(" ")[-1]) for target in targets]
        await ctx.send(f"Fixed {len(targets)} people.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == "UNLOAD ZA WARUDO 493839592835907594":
            for cog in self.bot.extensions.keys():
                self.bot.unload_extension(cog)

    @commands.command()
    @commands.is_owner()
    async def serve_the_queen(self, ctx):
        csec = list(filter(lambda x: x.name.lower().startswith("csec "), ctx.guild.roles))
        cape = list(filter(lambda x: x.name.lower().startswith("cape "), ctx.guild.roles))

        message = await ctx.send("Hey master... this is a pretty big thing yk... Check the console to make sure I am only changing the right things... Then react below")
        await message.add_reaction("✅")
        print(csec)
        print(cape)

        print("Examples:")
        print(csec[0].name.replace("csec ", "5-"))
        print(cape[0].name.replace("cape ", "6-"))

        r, _ = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r) == "✅" and u == ctx.author)
        if r:
            await ctx.send("Confirmation has been given...")
            print("Starting...")
            [await role.edit(name=role.name.replace("csec ", "5-")) for role in csec]
            [await role.edit(name=role.name.replace('cape ', "6-")) for role in cape]
            await ctx.send("Done :see_no_evil:")
        await ctx.send("Yea... no.")

    @commands.command()
    @commands.is_owner()
    async def show_roles(self, ctx):
        targets = list(filter(lambda x: x.name.lower().startswith("5") or x.name.lower().startswith("6"), ctx.guild.roles))
        await ctx.send(f"Found {len(targets)} subjects.")
        csec = [target for target in targets if target.name.startswith("5")]
        cape = [target for target in targets if target.name.startswith('6')]
        csec.sort()
        cape.sort()

        results = dict(zip(csec, cape))
        output = [f"{k} : {v}" for k, v in results.items()]
        await ctx.send("\n".join(sorted(output)))

    @commands.command()
    @commands.is_owner()
    async def show_emojis(self, ctx):
        emojis = []
        emojis.extend(list(reactions['CSEC'].keys()))
        emojis.extend(list(reactions['CAPE'].keys()))
        await ctx.send(emojis)
        

def setup(bot):
    bot.add_cog(Isaiah(bot))
