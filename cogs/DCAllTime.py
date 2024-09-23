import nextcord
from nextcord.ext import commands, tasks
from datetime import datetime, time
import pytz
import asyncio

DISCONNECT_TIME = time(6, 30)  # Set the time to 06:00 (6 AM) in EST
EST = pytz.timezone('US/Eastern')

class DisconnectCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = None
        self.voice_channel_id = None
        self.check_time.start()

    def cog_unload(self):
        self.check_time.cancel()

    @tasks.loop(seconds=60)
    async def check_time(self):
        if self.guild_id and self.voice_channel_id:
            now = datetime.now(EST).time()
            if now.hour == DISCONNECT_TIME.hour and now.minute == DISCONNECT_TIME.minute:
                await self.disconnect_all_members()
                await asyncio.sleep(60)  # Sleep for 60 seconds to prevent multiple disconnections in the same minute

    async def disconnect_all_members(self):
        guild = self.bot.get_guild(self.guild_id)
        voice_channel = guild.get_channel(self.voice_channel_id)
        if voice_channel:
            for member in voice_channel.members:
                await member.move_to(None)  # Disconnect the member

    @commands.command(name='setchannel')
    async def set_channel(self, ctx, channel: nextcord.VoiceChannel):
        self.guild_id = ctx.guild.id
        self.voice_channel_id = channel.id
        await ctx.send(f'Set the disconnect channel to: {channel.name} in guild: {ctx.guild.name}')
        
        
def setup(turtle):
    turtle.add_cog(DisconnectCog(turtle))