import nextcord
from nextcord.ext import commands
import yt_dlp as youtube_dl
import asyncio

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicView(nextcord.ui.View):
    def __init__(self, turtle, ctx):
        super().__init__(timeout=None)
        self.bot = turtle
        self.ctx = ctx

    @nextcord.ui.button(label="Pause", style=nextcord.ButtonStyle.primary)
    async def pause_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        voice_client = self.ctx.message.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Paused the music.", ephemeral=True)
        else:
            await interaction.response.send_message("No music is playing to pause.", ephemeral=True)

    @nextcord.ui.button(label="Resume", style=nextcord.ButtonStyle.primary)
    async def resume_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        voice_client = self.ctx.message.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Resumed the music.", ephemeral=True)
        else:
            await interaction.response.send_message("No music is paused to resume.", ephemeral=True)

    @nextcord.ui.button(label="Stop", style=nextcord.ButtonStyle.danger)
    async def stop_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        voice_client = self.ctx.message.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("Stopped the music.", ephemeral=True)
        else:
            await interaction.response.send_message("No music is playing to stop.", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, turtle):
        self.bot = turtle

    @commands.command(name='play', help='To play a song')
    async def play(self, ctx, url):
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.mention}, you need to be in a voice channel to play music!")
            return

        voice_channel = ctx.author.voice.channel
        print(f"User is in channel: {voice_channel}")

        if ctx.voice_client is None:
            print("Bot is not connected, trying to connect...")
            await voice_channel.connect()
        else:
            if ctx.voice_client.channel != voice_channel:
                print("Bot is in a different channel, moving...")
                await ctx.voice_client.move_to(voice_channel)

        voice_client = ctx.voice_client
        print(f"Bot is connected to: {voice_client.channel}")

        try:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

            await ctx.send(f'**Now playing:** {player.title}', view=MusicView(self.bot, ctx))
        except Exception as e:
            await ctx.send("An error occurred while trying to play the song.")
            print(e)

            
def setup(turtle):
    turtle.add_cog(Music(turtle))