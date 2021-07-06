import discord, asyncio, aiosqlite, random, re, sqlite3
from discord.ext import commands, tasks

columns = {
    "user_id": 0,
    "subject": 1,
    "title": 2,
    "tags": 3,
    "content": 4,
    "note_id": 5
}
class Notes(commands.Cog):
    """Ready to make some notes and see what other notes exist? Here are all the commands you need to do so"""
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.async_init())


    async def async_init(self):
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS NoteTable (
                user_id INTEGER,
                subject TEXT NOT NULL,
                title TEXT UNIQUE NOT NULL,
                tags TEXT NOT NULL,
                content TEXT NOT NULL,
                note_id INTEGER PRIMARY KEY AUTOINCREMENT
                )""")

            await db.commit()

    # Commands
    @commands.command(brief="Gives a quick tutorial on how to use p.takenote", help="Shows you how to use the p.takenote command to take notes for yourself and your fellow students")
    async def note(self, ctx):
        embed = discord.Embed(
            title="Here is an example on how to use p.takenote",
            description="p.takenote is a command that allows you to make a note for yourself and other users. Each note must have a title, tags to make it easy to find and of course, the content",
            color=random.randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="The Basic", value="The title of your note goes on the first line. The name of the subject the note refers to goes on the second line. The tags which it can be referenced by goes on the third line, and your content can have all the rest.", inline=False)
        embed.add_field(name="Format:", value="```\np.takenote\nSubject Name goes here\nYour Title goes here\nTags will go here.\nAnything this line and under is your content/note```",inline=False)
        embed.add_field(name="Example:", value="```\np.takenote\nPhysics\nMomentum\nmomentum, motion\nMomentum is a part of physics which relates to movement.\nMake sure that your notes are meaningful```")
        embed.set_footer(text="Then you just press enter and send the message. Easy isn't it. PS: It only counts as a new line once you press shift + enter (on pc) or move to the next line by pressing enter (on mobile)")

        await ctx.send(embed=embed)

    @commands.command(brief="Used to take notes for future reference", help="You can put up notes of your choice using this command so it can be accessed by any and all of your fellow students here in the hub. For usage information refer to p.note", usage="Subject, title, tags, content")
    async def takenote(self, ctx, *, your_note):
        your_note = your_note.split("\n")
        try:
            subject = your_note.pop(0).strip()
            title = your_note.pop(0).strip()
            tags = your_note.pop(0).strip()
            content = '\n'.join(your_note).strip()
        except IndexError:
            await ctx.send("Your note is invalid. Remember to put your Subject name, title, tags and content on separate lines as shown in p.note")
            return
    
        if len(content) < 5: await ctx.send("Your content is too short"); return
        
        await ctx.send("Processing your note")
        
        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("INSERT INTO NoteTable (user_id, subject, title, tags, content) VALUES (?, ?, ?, ?, ?)",
            (ctx.author.id, subject, title, tags, content))

            await db.commit()

        await ctx.send(f"Success. Saved your note as {title}")

        await asyncio.sleep(5)
        await ctx.message.delete()

    @commands.command(brief="Shows the titles for all available notes.", help="Shows a list of notes created by your fellow users")
    async def allnotes(self, ctx):
        rows = await self.fetch_all()

        to_send = [row[columns['title']] for row in rows]

        if not to_send: await ctx.send("No notes exist as yet. Make one with p.takenote. Use p.note for an example"); return
        
        to_send = list(set(to_send))
        await ctx.send('\n'.join(to_send))

    @commands.command(brief="Shows the titles of all notes created by you", help="Used to view a list of notes created by you or the person you mentioned.", usage="optional[@mention]")
    async def notesby(self, ctx, member:discord.Member=None):
        student = member or ctx.author

        db = await aiosqlite.connect("PCSGDB.sqlite3")
        cursor = await db.execute("SELECT * FROM NoteTable WHERE user_id == ?", (student.id, ))
        notes = await cursor.fetchall()

        await db.close()

        to_send = [note[columns['title']] for note in notes if note[columns['user_id']] == student.id]
        if not to_send: await ctx.send("I didn't seem to be able to find any notes created by you. Make some with p.takenote"); return
        
        to_send = list(set(to_send))
        await ctx.send('\n'.join(to_send))


    @commands.command(brief="Used to view a note", usage="[title of note or ID of note]", help="Use this to read a note created by you, or one of your fellow students here in the PCSG server.")
    async def getnote(self, ctx, *, tofind):
        notes = await self.fetch_all()
        if len(notes) == 0: await ctx.send("No notes have been made as yet"); return
        #to_send = [note for note in self.notes if tofind.lower() in [note.title.lower(), note.tags.lower()]]
        tofind = tofind.lower()
        to_send = [note for note in notes if tofind == note[columns['title']].lower().strip()]
        if not to_send:
            to_send = [note for note in notes if tofind == str(note[columns['note_id']]) or tofind in note[columns['title']].lower() or tofind in note[columns['tags']].lower() or tofind == note[columns['subject']].lower()]

        if not to_send: await ctx.send(f"Could not find a note containing {tofind}"); return
        if len(to_send) > 1: 
            await ctx.send("There is more than one match for your search. Here is a list of their titles and ids")
            titles = [{note[columns['title']]: note[columns["note_id"]]} for note in to_send]

            await ctx.send('\n'.join(titles[:25]))
            return

        to_send = to_send[0]
        person = discord.utils.get(ctx.guild.members, id=to_send[columns['user_id']])
        if person:
            name = person.name
        else:
            name = "Forgotten User"
        embed = discord.Embed(
            title=f"Subject: {to_send[columns['subject']]}\nTitle: {to_send[columns['title']]}",
            description=f"Content: {to_send[columns['content']]}",
            color=random.randint(0, 0xffffff)
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Tags:", value=to_send[columns['tags']])
        embed.add_field(name="Note ID:", value=to_send[columns['note_id']])
        embed.set_footer(text=f"Showing note by {name}.")

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🥱")
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '🥱'
        try:
            _, _ = await self.bot.wait_for("reaction_add", timeout=300, check=check)
        except asyncio.TimeoutError:
            pass
        await msg.delete()

    @commands.command(brief="Deletes a note created by yourself", help="Wish to take down a note belonging to you (or anyone if you are a mod), then you can use this command to do it.", usage="Note Title or ID")
    async def delnote(self, ctx, *, note_to_delete):
        notes = await self.fetch_all()
        if len(notes) == 0: await ctx.send("No notes have been made as yet"); return
        
        to_del = [note for note in notes if note[columns['title']].lower().strip() == note_to_delete.lower().strip()]
        
        if not to_del: await ctx.send("Could not find a note with that title"); return
        
        to_del = to_del[0]
        your_moderators = [member for member in ctx.guild.members if member.guild_permission.manage_messages or member.id == to_del[columns['user_id']]]
        
        if not ctx.author.id in your_moderators: 
            await ctx.send("You do not have permission to delete this note.")
            return

        async with aiosqlite.connect("PCSGDB.sqlite3") as db:
            await db.execute("DELETE FROM NoteTable WHERE note_id = ?", (str(to_del['note_id']),))
            await db.commit()

        person = discord.utils.get(ctx.guild.members, id=to_del['user_id'])
        if person: name = person.name
        else: name = "Unknown User"
        await ctx.send(f"Deleted {name}'s note on {to_del[columns['title']]}")      

    async def fetch_all(self):
        db = await aiosqlite.connect("PCSGDB.sqlite3")
        cursor = await db.execute("SELECT * FROM NoteTable")
        rows = await cursor.fetchall()
        await db.close()
        
        return rows

def setup(bot):
    bot.add_cog(Notes(bot))