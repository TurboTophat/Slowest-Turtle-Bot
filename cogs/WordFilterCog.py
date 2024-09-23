import nextcord
import re
import logging
from nextcord.ext import commands
from langdetect import detect, LangDetectException

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordFilterCog(commands.Cog):
    def __init__(self, turtle):
        self.bot = turtle
        self.forbidden_words = self.load_forbidden_words()  # Load forbidden words from file

    def load_forbidden_words(self):
        forbidden_words = []
        try:
            with open("./cogs/forbidden_words.txt", "r") as file:
                for line in file:
                    forbidden_words.append(line.strip())  # Remove newline characters and add to list
        except FileNotFoundError:
            logger.error("Forbidden words file not found.")
        return forbidden_words

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  # Ignore messages sent by bots
            return
        
        try:
            detected_lang = detect(message.content)
        except LangDetectException:
            detected_lang = 'unknown'
        
        logger.info(f"Detected language: {detected_lang} for message: {message.content}")

        # Check for forbidden words in English or Polish
        if detected_lang in ['en', 'pl']:
            logger.info(f"Detected {detected_lang.upper()} message: {message.content}")
            for word in self.forbidden_words:
                pattern = re.compile(fr"\b{word}\b", flags=re.IGNORECASE)
                if pattern.search(message.content):
                    logger.info(f"Forbidden word detected: {word}")
                    try:
                        await message.delete()
                        await message.channel.send(content=f"{message.author.mention}, please refrain from using inappropriate language.", allowed_mentions=nextcord.AllowedMentions(users=False))
                        logger.info(f"Deleted message from {message.author} in channel {message.channel.name}")
                    except nextcord.Forbidden:
                        logger.error(f"Missing permissions to delete messages or send messages in channel: {message.channel.name}")
                    break

def setup(turtle):
    turtle.add_cog(WordFilterCog(turtle))