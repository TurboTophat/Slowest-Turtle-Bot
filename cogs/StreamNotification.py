import os
from apikeys import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET
from nextcord.ext import tasks, commands
import aiohttp
import json

class StreamNotification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_client_id = TWITCH_CLIENT_ID
        self.twitch_client_secret = TWITCH_CLIENT_SECRET
        self.auth_token = None
        self.streamers = []  # List of Twitch usernames
        self.live_streams = {}  # Dictionary to track live status {twitch_username: live_status}
        self.notification_channel_id = None
        self.load_channel_id()
        self.check_streams.start()  # Start the task loop

    async def get_twitch_token(self):
        """Get an OAuth token for Twitch API."""
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
        """Check if a Twitch streamer is live."""
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
                return bool(data['data'])  # Stream is live if there's data

    @commands.command(name='setlivechannel')
    async def set_channel(self, ctx, channel: commands.TextChannelConverter):
        """Sets the channel where live notifications will be sent."""
        self.notification_channel_id = channel.id
        self.save_channel_id(channel.id)
        await ctx.send(f"Live notifications will be sent to {channel.mention}")

    @commands.command(name='addstreamer')
    async def add_streamer(self, ctx, twitch_username: str):
        """Add a Twitch streamer to the watch list."""
        if twitch_username not in self.streamers:
            self.streamers.append(twitch_username)
            self.live_streams[twitch_username] = False  # Assume not live initially
            await ctx.send(f"Added {twitch_username} to the streamer watch list!")
        else:
            await ctx.send(f"{twitch_username} is already on the watch list!")

    @commands.command(name='removestreamer')
    async def remove_streamer(self, ctx, twitch_username: str):
        """Remove a Twitch streamer from the watch list."""
        if twitch_username in self.streamers:
            self.streamers.remove(twitch_username)
            del self.live_streams[twitch_username]  # Remove their live status tracking
            await ctx.send(f"Removed {twitch_username} from the watch list.")
        else:
            await ctx.send(f"{twitch_username} is not on the watch list.")

    @tasks.loop(minutes=5)  # Check every 5 minutes
    async def check_streams(self):
        """Periodically check if streamers in the list are live."""
        if not self.auth_token:
            await self.get_twitch_token()

        # Loop through each registered streamer
        for streamer_name in self.streamers:
            is_live = await self.is_stream_live(streamer_name)

            # If the stream is live and wasn't already marked as live
            if is_live and not self.live_streams.get(streamer_name, False):
                self.live_streams[streamer_name] = True  # Mark as live
                await self.notify_live(streamer_name)

            # If the stream is no longer live, reset live status
            elif not is_live and self.live_streams.get(streamer_name, False):
                self.live_streams[streamer_name] = False  # Mark as not live

    async def notify_live(self, streamer_name):
        """Notify the channel that a streamer has gone live."""
        if self.notification_channel_id:
            channel = self.bot.get_channel(self.notification_channel_id)
            if channel:
                await channel.send(f"@everyone, {streamer_name} is now live! Watch here: https://www.twitch.tv/{streamer_name}")

    # Save the notification channel ID to a file
    def save_channel_id(self, channel_id):
        with open("channel_config.json", "w") as file:
            json.dump({"channel_id": channel_id}, file)

    # Load the notification channel ID from the file
    def load_channel_id(self):
        try:
            with open("channel_config.json", "r") as file:
                data = json.load(file)
                self.notification_channel_id = data.get("channel_id")
        except FileNotFoundError:
            self.notification_channel_id = None

    @check_streams.before_loop
    async def before_check_streams(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()

def setup(turtle):
    turtle.add_cog(StreamNotification(turtle))