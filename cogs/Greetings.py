import nextcord
from nextcord.ext import commands


class Greetings(commands.Cog):
    def __init__(self, turtle):
        self.bot = turtle
        self._last_member = None
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = nextcord.utils.get(member.guild.channels, name="welcome")
        await channel.send(f"Hello {member.mention}, Welcome To Nowhere")


    discordserverid = 1218021480483520592
# making a cog change the bots name to Commnads instaed
    @nextcord.slash_command(guild_ids=[discordserverid], description="Say hello with a slash command")
    async def hello(self, ctx, *, member: nextcord.Member = None):
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f"Hello {member.name}, i am the turtle bot.")
    # await ctx.send("Hello, i am the turtle bot.")

def setup(turtle):
    turtle.add_cog(Greetings(turtle))