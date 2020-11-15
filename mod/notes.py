import discord, asyncio, aiosqlite, random, re
from discord.ext import commands, tasks

class Noting(commands.Cog):
    """All commands relating to notes"""
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    notes = []

    async def async_init(self):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS Notes (
                user_id INTEGER,
                title TEXT PRIMARY KEY UNIQUE NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL
                )""")

            await db.commit()

        await self.setup()
        self.saving.start()

    async def setup(self):
        keys = ['user_id', 'title', 'content', 'tags']
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            async with db.execute("SELECT * FROM Notes") as cursor:
                if not cursor: print("No Data to set up with"); return
                async for row in cursor:
                    values = [row[0], row[1], row[2], row[3]]
                    note = dict(zip(keys, values))

                    self.notes.append(note)

        print("Setup was successful")

    # Commands
    @commands.command(brief="Gives a quick tutorial on how to use p.takenote", help="Shows you how to use the p.takenote command to take notes for yourself and your fellow students")
    async def note(self, ctx):
        embed = discord.Embed(
            title="Here is an example on how to use p.takenote",
            description="p.takenote is a command that allows you to make a note for yourself and other users. Each note must have a title, tags to make it easy to find and of course, the content",
            color=random.randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="The Basic", value="The title of your note goes on the first line. The tags which it can be referenced by goes on the second line, and your content can have all the rest.", inline=False)
        embed.add_field(name="Example:", value="p.takenote\nTitle: Momentum\nTags: physics, momentum, motion\nContent: Momentum is a part of physics which relates to movement")
        embed.set_footer(text="Then you just press enter and send the message. Easy isn't it. The Content is the last thing you should do")

        await ctx.send(embed=embed)

    @commands.command(brief="Used to take notes for future reference", help="You can put up notes of your choice using this command so it can be accessed by any and all of your fellow students here in the hub. For usage information refer to p.note", usage="title, tags, content")
    async def takenote(self, ctx, *, noted):
        noted = noted.split("\n")
        try:
            title = noted.pop(0)
            tags = noted.pop(0)
            content = '\n'.join(noted)
        except IndexError:
            await ctx.send("Your note is invalid. Remember to put your title, tags and content on separate lines as shown in p.note")
            return
    
        if len(content) < 5: await ctx.send("Your content is too short"); return
        
        await ctx.send("Processing your note")
        if len(self.notes) > 1:
            for check in self.notes:
                if check['title'].lower() == title.lower(): await ctx.send("A note with this Title already exists"); return
        
        mylist = ["user_id", "title", "content", "tags"]
        value = [ctx.author.id, title, content, tags]
        
        # Before knowing about dict comprehensions
        # note = {}
        # for i, v in enumerate(mylist):
        #     note[v] = value[i]

        # After Learning about Dict Comprehensions
        note = dict(zip(mylist, value))
            

        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("INSERT INTO Notes (user_id, title, content, tags) VALUES (?, ?, ?, ?)",
            (ctx.author.id, title, content, tags))

        await ctx.send("Success")

        self.notes.append(note)

    @commands.command(brief="Shows the titles for all available notes.", help="Shows a list of notes created by your fellow users")
    async def allnotes(self, ctx):
        to_send = [note['title'] for note in self.notes]
        if not to_send: await ctx.send("No notes exist as yet. Make one with p.takenote. Use p.note for an example"); return
        to_send = list(set(to_send))
        await ctx.send(f"**__{', '.join(to_send)}__**")

    @commands.command(brief="Shows the titles of all of your notes", help="Used to view a list of notes created by you")
    async def mynotes(self, ctx):
        to_send = [note['title'] for note in self.notes if note['user_id'] == ctx.author.id]
        if not to_send: await ctx.send("I didn't seem to be able to find any notes created by you. Make some with p.takenote"); return
        to_send = list(set(to_send))
        await ctx.send(f"**__{', '.join(to_send)}__**")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def deldbnotes(self, ctx):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("DROP TABLE IF EXISTS Notes")

            await db.commit()

        await ctx.send("Deleted Notes table")

    @commands.command(brief="Used to view a note", usage="[title of note] or [ID of note]", help="Use this to read a note created by you, or one of your fellow students here in the PCSG server.")
    async def getnote(self, ctx, *, tofind):
        if len(self.notes) == 0: await ctx.send("No notes have been made as yet"); return
        #to_send = [note for note in self.notes if tofind.lower() in [note.title.lower(), note.tags.lower()]]
        tofind = tofind.lower()
        to_send = [note for note in self.notes if tofind in note['title'].lower() or tofind in note['tags'].lower()]

        # to_send = []
        # for note in self.notes:
        #     if tofind.lower() in note.title.lower() or tofind.lower() in note.tags.lower(): to_send.append(note)

        if not to_send: await ctx.send(f"Could not find a note with containing {tofind}"); return
        if len(to_send) > 1: 
            await ctx.send("There is more than one match for your search. Here is a list of their titles")
            titles = [note['title'] for note in to_send]

            await ctx.send(', '.join(titles[:25]))
            return

        to_send = to_send[0]
        person = discord.utils.get(ctx.guild.members, id=to_send['user_id'])
        if person:
            name = person.name
        else:
            name = "Forgotten User"
        embed = discord.Embed(
            title=f"Title: {to_send['title']}",
            description=f"Content: {to_send['content']}",
            color=random.randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Tags:", value=to_send['tags'])
        embed.set_footer(text=f"Showing note by {name}.")

        await ctx.send(embed=embed)

    @commands.command(brief="Deletes a note created by yourself", help="Wish to take down a note belonging to you (or anyone if you are a mod), then you can use this command to do it.", usage="Title of note")
    async def delnote(self, ctx, notetodel):
        if len(self.notes) == 0: await ctx.send("No notes have been made as yet"); return
        
        to_del = [note for note in self.notes if note['title'].lower() == notetodel.lower()]

        if not to_del: await ctx.send("Could not find a note with that id"); return
        your_moderators = [352461326800519169, 493839592835907594, 691653525335441428, 315856223130091520, 693241262915977236, to_del.user_id]
        if not ctx.author.id in your_moderators: 
            await ctx.send("You do not have permission to delete this note.")
            return

        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("DELETE FROM Notes WHERE title = ?", (to_del['title'],))
            await db.commit()
        person = discord.utils.get(ctx.guild.members, id=to_del['user_id'])
        if person: name = person.name
        else: name = "Unknown User"
        await ctx.send(f"Deleted {name}'s note on {to_del.title}")      
        self.notes.remove(to_del)
        del to_del   

    # Saving
    @tasks.loop(minutes=2)
    async def saving(self):
        if len(self.notes) > 1:
            async with aiosqlite.connect("PCSGDB.sqlite3") as db:
                for note in self.notes:
                    await db.execute("INSERT OR REPLACE INTO Notes (user_id, title, content, tags) VALUES (?, ?, ?, ?)",
                    (note['user_id'], note['title'], note['content'], note['tags']))

                await db.commit()
    

def setup(bot):
    bot.add_cog(Noting(bot))