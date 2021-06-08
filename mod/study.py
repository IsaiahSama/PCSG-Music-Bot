from discord.ext import commands
from mydicts import resource_categories, csec_subjects

class Study(commands.Cog):
    """ All the commands you need to give you access to the resources you want """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Provides links to past paper solutions", help="Used to instantly provide a link to past paper solutions")
    async def sol(self, ctx):
        await ctx.send("https://www.pastpapersforall.online/solutions <- Get your solutions here")

    @commands.command(brief="GEts the link where you can view mark schemes", help="Command that gives you the link for the mark schemes")
    async def mark(self, ctx):
        await ctx.send("https://www.pastpapersforall.online/markschemes <- View mark schemes here")

    @commands.command(brief="Provides links to past papers", help="Used to instantly provide a link to past papers for subjects.", usage="(csec or cape) name_of_subject")
    async def pp(self, ctx, proficiency, *, subject_name):
        """ Attempts to find past papers for a given subject """

        proficiency = proficiency.lower()

        if proficiency not in ["csec", "cape"]:
            await ctx.send("Your proficiency must be either `csec` or `cape`")
            return
        
        if proficiency == "cape":
            await ctx.send("Sorry, but cape past papers are within google drives. Please visit here for them: https://www.pastpapersforall.online/pastpapers#h.gpa9rpry7b8")
            return

        base_url = "https://www.csecpastpapers.com/"

        potentials = [subject for subject in csec_subjects.keys() if subject in subject_name]

        await ctx.send(f"Getting all relevant matches for {ctx.author.mention}")
        for potential in potentials:
            await ctx.send(base_url + csec_subjects[potential])

    @commands.command(brief="Used to find resources for a subject", usage="proficiency (csec or cape) name of subject")
    async def resource(self, ctx, proficiency, *, subject_name):
        """Attempts to find resources for a given subject name"""

        if proficiency.lower() not in ["csec", "cape"]:
            await ctx.send("`proficiency` must be CSEC or CAPE")
            return

        to_search = resource_categories[proficiency.upper()]

        subjects = {}
        for topic, subject_list in to_search.items():
            for subject in subject_list:
                if subject_name.lower() in subject:
                    subjects[topic] = subject
        
        if subjects:
            base_url = "https://www.ppresources.online/"
            for topic, subject in subjects.items():
                url = base_url + f"{proficiency.lower()}/{proficiency.lower()}-{topic.lower()}/{subject.replace(' ', '-').lower()}"
                await ctx.send(url)
        else:
            await ctx.send(f"Could not find a {subject_name} resource in the {proficiency} category")

def setup(bot):
    bot.add_cog(Study(bot))