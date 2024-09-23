import nextcord
from nextcord.ext import commands

class VoiceChannel(commands.Cog):
    def __init__(self, turtle):
        self.bot = turtle
        self._last_member = None

    @commands.command(pass_context=True)
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not in Voice chat, You must be in a Voice chat to use this Command.")

    @commands.command(pass_context=True)
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.send("I've left the Voice chat")
        else:
            await ctx.send("I'm not a Voice chat")


def setup(turtle):
    turtle.add_cog(VoiceChannel(turtle))