import nextcord
from nextcord.ext import commands

class Reactions(commands.Cog):
    def __init__(self, turtle):
        self.bot = turtle
        self._last_member = None

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        channel = reaction.message.channel
        await channel.send(user.name + " Added: " + reaction.emoji)
        
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        channel = reaction.message.channel
        await channel.send(user.name + " Removed: " + reaction.emoji)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        if "happy" in message.content.lower():
            emoji = "😊"
            await message.add_reaction(emoji)

  
def setup(turtle):
    turtle.add_cog(Reactions(turtle))