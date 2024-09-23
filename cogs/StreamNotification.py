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
        self.streamers = {}  # {discord_user_id: [twitch_username_1, twitch_username_2]}
        self.live_streams = {}  # {twitch_username: live_status}
        self.notification_channel_id = None
        self.load_channel_id()
        self.check_stream.start()

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
                if data['data']:  # Stream is live if there's data
                    return True
                return False

    @commands.command(name='addstreamer')
    async def add_streamer(self, ctx, twitch_username: str):
        """Add a Twitch streamer to the watch list."""
        if ctx.author.id not in self.streamers:
            self.streamers[ctx.author.id] = []
        if twitch_username not in self.streamers[ctx.author.id]:
            self.streamers[ctx.author.id].append(twitch_username)
            self.live_streams[twitch_username] = False  # Assume not live initially
            await ctx.send(f"Added {twitch_username} to your watch list!")
        else:
            await ctx.send(f"{twitch_username} is already on your list!")

    @commands.command(name='removestreamer')
    async def remove_streamer(self, ctx, twitch_username: str):
        """Remove a Twitch streamer from the watch list by name."""
        if ctx.author.id in self.streamers and twitch_username in self.streamers[ctx.author.id]:
            self.streamers[ctx.author.id].remove(twitch_username)
            # Optionally remove the streamer from the live_streams tracking
            if twitch_username in self.live_streams:
                del self.live_streams[twitch_username]
            await ctx.send(f"Removed {twitch_username} from your watch list.")
        else:
            await ctx.send(f"{twitch_username} is not on your list.")

    @tasks.loop(minutes=5)  # Check every 5 minutes
    async def check_stream(self):
        """Periodically check if streamers are live."""
        if not self.auth_token:
            await self.get_twitch_token()

        # Loop through each registered streamer
        for user_id, streamers in self.streamers.items():
            for streamer_name in streamers:
                is_live = await self.is_stream_live(streamer_name)
                
                # If the stream is live and wasn't already live
                if is_live and not self.live_streams.get(streamer_name, False):
                    self.live_streams[streamer_name] = True  # Mark as live
                    # Send notification to Discord channel
                    channel = nextcord.utils.get(self.bot.get_all_channels(), name='stream-notifications')
                    if channel:
                        await channel.send(f"@everyone, {streamer_name} is now live! Watch here: https://www.twitch.tv/{streamer_name}")

                # If the stream is not live anymore, reset the live status
                elif not is_live and self.live_streams.get(streamer_name, False):
                    self.live_streams[streamer_name] = False  # Mark as not live

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

    @check_stream.before_loop
    async def before_check_stream(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()

def setup(turtle):
    turtle.add_cog(StreamNotification(turtle))