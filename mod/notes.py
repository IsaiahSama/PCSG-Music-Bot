import discord, asyncio, aiosqlite, random, re
from discord.ext import commands, tasks

class Notes:
    def __init__(self, name=None, user_id=None, title=None, content=None, tags=None, post_id=None):
        self.name = name
        self.user_id = user_id
        self.title = title
        self.content = content
        self.tags = tags
        self.post_id = post_id

class Noting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())

    notes = []

    async def async_init(self):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS Notes (
                name TEXT,
                user_id INTEGER,
                title TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL,
                post_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL 
                )""")

            await db.commit()

        await self.setup()
        self.saving.start()

    async def setup(self):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            async with db.execute("SELECT * FROM Notes") as cursor:
                if not cursor: print("No Data to set up with"); return
                async for row in cursor:
                    note = Notes(*row)

                    self.notes.append(note)

        print("Setup was successful")

    # Commands
    @commands.command()
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

    @commands.command()
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
                if check.title.lower() == title.lower(): await ctx.send("A note with this Title already exists"); return
        
        mylist = ["name", "user_id", "title", "content", "tags"]
        value = [str(ctx.author), ctx.author.id, title, content, tags]
        
        note = Notes()
        for i, v in enumerate(mylist):
            setattr(note, v, value[i])

        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("INSERT INTO Notes (name, user_id, title, content, tags) VALUES (?, ?, ?, ?, ?)",
            (str(ctx.author), ctx.author.id, title, content, tags))

            await db.commit()

            async with db.execute("SELECT post_id from Notes WHERE title = ? and user_id = ?", (title, ctx.author.id)) as cur:
                async for row in cur:
                    note.post_id = row[0]
                    break

        await ctx.send("Success")

        self.notes.append(note)

    @commands.command()
    async def allnotes(self, ctx):
        to_send = [note.title for note in self.notes]
        await ctx.send(', '.join(to_send))

    @commands.command()
    @commands.is_owner()
    async def deldbnotes(self, ctx):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("DROP TABLE IF EXISTS Notes")

            await db.commit()

        await ctx.send("Deleted Notes table")

    @commands.command()
    async def getnote(self, ctx, *, tofind):
        if len(self.notes) == 0: await ctx.send("No notes have been made as yet"); return
        #to_send = [note for note in self.notes if tofind.lower() in [note.title.lower(), note.tags.lower()]]
        to_send = []
        for note in self.notes:
            if tofind.lower() in note.title.lower() or tofind.lower() in note.tags.lower(): to_send.append(note)

        if not to_send: await ctx.send(f"Could not find a note with containing {tofind}"); return
        if len(to_send) > 1: 
            await ctx.send("There is more than one match for your search. Here is a list of their titles")
            titles = [note_title.title for note_title in to_send]

            await ctx.send(', '.join(titles[:25]))
            return

        to_send = to_send[0]
        embed = discord.Embed(
            title=f"Showing note by {to_send.name}.\nTitle: {to_send.title}",
            description=f"Content: {to_send.content}",
            color=random.randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Tags", value=to_send.tags)
        embed.add_field(name="ID", value=to_send.post_id)

        await ctx.send(embed=embed)

    @commands.command()
    async def delnote(self, ctx, idtodel: int):
        if len(self.notes) == 0: await ctx.send("No notes have been made as yet"); return
        to_del = None
        for note in self.notes:
            if note.post_id == idtodel: to_del = note; break

        if not to_del: await ctx.send("Could not find a note with that id"); return
        await ctx.send(f"Deleted {to_del.name}'s note on {to_del.title}")      
        self.notes.remove(to_del)
        del to_del   

    # Saving
    @tasks.loop(minutes=10)
    async def saving(self):
        if len(self.notes) > 1:
            async with aiosqlite.connect("PCSGDB.sqlite3") as db:
                for note in self.notes:
                    await db.execute("INSERT OR REPLACE INTO Notes (name, user_id, title, content, tags, post_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (note.name, note.user_id, note.title, note.content, note.tags, note.post_id))

                await db.commit()
    

def setup(bot):
    bot.add_cog(Noting(bot))