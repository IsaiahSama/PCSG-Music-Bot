import discord, asyncio, random
from discord.ext import commands

class Polling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    active_polls = []

    @commands.command(help="Make a poll for users to vote on. Options for the poll must first start with an emoji of your choice, then the poll option. Each option must go on a new line.")
    async def makepoll(self, ctx, *, pollmsg):
        poll = pollmsg.split("\n")
        if not len(poll) > 1:
            await ctx.send("You must have at least 2 options to have a valid poll.")
            return

        if len(poll) > 10: await ctx.send("You have too many values for this poll."); return

        content = {}
        for line in poll:
            content[line[0]] = line[1:].strip()

        pollbed = discord.Embed(
            title=f"Poll Created by {ctx.author}",
            color=random.randint(0, 0xffffff)
        )

        pollbed.set_thumbnail(url=ctx.author.avatar_url)
        pollbed.set_footer(text="React to give your feedback.")

        for k, v in content.items():
            pollbed.add_field(name=f"Option: {v}", value=f"Reaction: {k}", inline=False)


        old_msg = await ctx.send(embed=pollbed)

        for v in content.keys():
            try:
                await old_msg.add_reaction(v)
            except discord.HTTPException:
                await ctx.send(f"{v} is an invalid emoji. So your poll has been cancelled")
                return

        await ctx.send("I'll let you know results in 30 minutes")

        await asyncio.sleep(1800)
        
        msg = await ctx.channel.fetch_message(old_msg.id)
        allreactions = msg.reactions

        valid_reactions = [reaction for reaction in allreactions if str(reaction) in content.keys()]

        highest = 0
        winner = None
        for reaction in valid_reactions:
            if reaction.count > highest:
                winner = reaction
                highest = winner.count

        await ctx.send(f"{ctx.author.mention}, Your poll is complete. Winner is {content[winner.emoji]} with {winner.count} votes")


def setup(bot):
    bot.add_cog(Polling(bot))
