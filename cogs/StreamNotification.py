import nextcord
from nextcord.ext import tasks, commands
import aiohttp
import json
from apikeys import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET

class StreamNotification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_client_id = TWITCH_CLIENT_ID
        self.twitch_client_secret = TWITCH_CLIENT_SECRET
        self.auth_token = None
        self.streamers = {}  # {discord_user_id: twitch_username}
        self.live_streams = {}  # {twitch_username: live_status}
        self.notification_channel_id = None
        self.load_channel_id()  # Load saved channel ID
        self.check_stream.start()  # Start checking streams when bot starts

    async def get_twitch_token(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://id.twitch.tv/oauth2/token',
                params={
                    'client_id': self.twitch_client_id,
                    'client_secret': self.twitch_client_secret,
                    'grant_type': 'client_credentials',
                }
            ) as response:
                data = await response.json()
                self.auth_token = data['access_token']

    async def is_stream_live(self, streamer_name):
        headers = {
            'Client-ID': self.twitch_client_id,
            'Authorization': f'Bearer {self.auth_token}',
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://api.twitch.tv/helix/streams?user_login={streamer_name}',
                headers=headers
            ) as response:
                data = await response.json()
                if data['data']:  # Stream is live if there's data
                    return True
                return False

    @commands.command(name='setlivechannel')
    async def set_channel(self, ctx, channel: nextcord.TextChannel = None):
        """Sets the channel where live notifications will be sent."""
        if channel is None:
            await ctx.send("Please specify a channel, e.g., `!setlivechannel #your-channel-name`.")
            return
    
        self.notification_channel_id = channel.id
        self.save_channel_id(channel.id)  # Save the channel ID
        await ctx.send(f"Live notifications will be sent to {channel.mention}")

    @commands.command(name='addstreamer')
    async def add_streamer(self, ctx, twitch_username: str):
        self.streamers[ctx.author.id] = twitch_username
        self.live_streams[twitch_username] = False  # Assume not live initially
        await ctx.send(f"Added {twitch_username} to the streamer watch list!")

    @commands.command(name='removestreamer')
    async def remove_streamer(self, ctx):
        """Removes the Twitch streamer for the user."""
        if ctx.author.id in self.streamers:
            del self.streamers[ctx.author.id]
            await ctx.send(f"Removed your streamer from the watch list.")
        else:
            await ctx.send("You don't have a streamer registered.")

    @tasks.loop(minutes=5)  # Check every 5 minutes
    async def check_stream(self):
        """Periodically check if streamers are live."""
        if not self.auth_token:
            await self.get_twitch_token()

        for user_id, streamer_name in self.streamers.items():
            is_live = await self.is_stream_live(streamer_name)
            if is_live and not self.live_streams.get(streamer_name, False):
                self.live_streams[streamer_name] = True
                channel = self.bot.get_channel(self.notification_channel_id)
                if channel:
                    user = self.bot.get_user(user_id)
                    await channel.send(f"@everyone, {streamer_name} is now live! Watch here: https://www.twitch.tv/{streamer_name}")
            elif not is_live and self.live_streams.get(streamer_name, False):
                self.live_streams[streamer_name] = False

    def save_channel_id(self, channel_id):
        with open("channel_config.json", "w") as file:
            json.dump({"channel_id": channel_id}, file)

    def load_channel_id(self):
        try:
            with open("channel_config.json", "r") as file:
                data = json.load(file)
                self.notification_channel_id = data.get("channel_id")
        except FileNotFoundError:
            self.notification_channel_id = None

    @check_stream.before_loop
    async def before_check_stream(self):
        await self.bot.wait_until_ready()

def setup(turtle):
    turtle.add_cog(StreamNotification(turtle))