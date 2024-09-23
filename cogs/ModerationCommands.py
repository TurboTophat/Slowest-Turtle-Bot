import nextcord
from nextcord.ext import commands

class ModerationCommands(commands.Cog):
    def __init__(self, turtle):
        self.bot = turtle
        self._last_member = None

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: nextcord.Member, *, reason=None):
        channel = nextcord.utils.get(member.guild.channels, name="bot-testing")
        await member.kick(reason=reason)
        if channel:  # Check if the channel exists
            await channel.send(f"User {member.mention} has been kicked.")
            await ctx.message.delete()  # Delete the original command message
        else:
            await ctx.send("Couldn't find the specified channel.")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention} You need premissions to kick people.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Could not find the specified member.")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: nextcord.Member, *, reason=None):
        channel = nextcord.utils.get(member.guild.channels, name="bot-testing")
        await member.ban(reason=reason)
        if channel:  # Check if the channel exists
            await channel.send(f"User {member.mention} has been banned.")
            await ctx.message.delete()  # Delete the original command message
        else:
            await ctx.send("Couldn't find the specified channel.")

       # await ctx.send(f"User {member.mention} Has Been Banned")


    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}You need premissions to ban people.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Could not find the specified member.")
        
def setup(turtle):
    turtle.add_cog(ModerationCommands(turtle))