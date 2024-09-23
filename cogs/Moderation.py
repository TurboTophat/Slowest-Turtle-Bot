import nextcord
from nextcord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, turtle):
        self.bot = turtle
        self._last_member = None
        
        

def setup(turtle):
    turtle.add_cog(Moderation(turtle))