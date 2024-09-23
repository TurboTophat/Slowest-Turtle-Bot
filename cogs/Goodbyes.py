import nextcord
from nextcord.ext import commands

class Goodbyes(commands.Cog):
    def __init__(self, turtle):
        self.bot = turtle
        self._last_member = None
        
    # all events change to this will make it work
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = nextcord.utils.get(member.guild.channels, name='goodbye')
        await channel.send(f"Thank You, Come Again. {member.mention}")
    
    discordserverid = 1218021480483520592
    # Text on how to make a custom command prefix to get the bot to say hello ect...
    # making a cog change the bots name to Commnads instaed    
    @nextcord.slash_command(guild_ids=[discordserverid], description="Say Goodbye with a slash command")
    async def bye(self, ctx, *, member: nextcord.Member = None):
        await ctx.send(f"Goodbye {member.name}, Hope to talk to you again.")

def setup(turtle):
    turtle.add_cog(Goodbyes(turtle))