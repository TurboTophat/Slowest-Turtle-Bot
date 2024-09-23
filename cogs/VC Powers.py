import nextcord
from nextcord.ext import commands

class Disconnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dc')
    async def dc(self, ctx, member: nextcord.Member):
        if not ctx.author.guild_permissions.move_members:
            await ctx.send("You don't have permission to disconnect members!")
            return

        if member.voice and member.voice.channel:
            await member.move_to(None)
            await ctx.send(f'{member.display_name} has been disconnected from the voice channel.')
        else:
            await ctx.send(f'{member.display_name} is not in a voice channel!')

    @commands.command(name='mute')
    async def mute(self, ctx, member: nextcord.Member):
        if not ctx.author.guild_permissions.mute_members:
            await ctx.send("You don't have permission to mute members!")
            return

        if member.voice and not member.voice.mute:
            await member.edit(mute=True)
            await ctx.send(f'{member.display_name} has been muted.')
        else:
            await ctx.send(f'{member.display_name} is either not in a voice channel or already muted!')

    @commands.command(name='unmute')
    async def unmute(self, ctx, member: nextcord.Member):
        if not ctx.author.guild_permissions.mute_members:
            await ctx.send("You don't have permission to unmute members!")
            return

        if member.voice and member.voice.mute:
            await member.edit(mute=False)
            await ctx.send(f'{member.display_name} has been unmuted.')
        else:
            await ctx.send(f'{member.display_name} is either not in a voice channel or not muted!')

    @commands.command(name='deafen')
    async def deafen(self, ctx, member: nextcord.Member):
        if not ctx.author.guild_permissions.deafen_members:
            await ctx.send("You don't have permission to deafen members!")
            return

        if member.voice and not member.voice.deaf:
            await member.edit(deafen=True)
            await ctx.send(f'{member.display_name} has been deafened.')
        else:
            await ctx.send(f'{member.display_name} is either not in a voice channel or already deafened!')

    @commands.command(name='undeafen')
    async def undeafen(self, ctx, member: nextcord.Member):
        if not ctx.author.guild_permissions.deafen_members:
            await ctx.send("You don't have permission to undeafen members!")
            return

        if member.voice and member.voice.deaf:
            await member.edit(deafen=False)
            await ctx.send(f'{member.display_name} has been undeafened.')
        else:
            await ctx.send(f'{member.display_name} is either not in a voice channel or not deafened!')

    @commands.command(name='move')
    async def move(self, ctx, member: nextcord.Member, *, channel_name: str):
        if not ctx.author.guild_permissions.move_members:
            await ctx.send("You don't have permission to move members!")
            return

        if member.voice and member.voice.channel:
            # Convert channel names to lowercase for case-insensitive comparison
            channel_name_lower = channel_name.lower()
            channels = [vc for vc in ctx.guild.voice_channels if vc.name.lower() == channel_name_lower]

            if not channels:
                await ctx.send(f'Channel "{channel_name}" not found in this server!')
                return

            # Assuming there's only one matching channel, otherwise you can handle it accordingly
            channel = channels[0]

            await member.move_to(channel)
            await ctx.send(f'{member.display_name} has been moved to {channel.name}.')
        else:
            await ctx.send(f'{member.display_name} is not in a voice channel!')


def setup(turtle):
    turtle.add_cog(Disconnect(turtle))