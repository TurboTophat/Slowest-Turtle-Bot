import nextcord
from nextcord.ext import commands
import os

from apikeys import BOTTOKEN

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True

turtle = commands.Bot(command_prefix="t.", intents=intents)


@turtle.event
async def on_ready():
    await turtle.change_presence(
        status=nextcord.Status.do_not_disturb,
        activity=nextcord.Activity(type= nextcord.ActivityType.listening, name= "Slowest turtle Podcast"),
    )
    #   turtle.loop.create_task(node_connect())
    print(f"Logged in as {turtle.user} (ID: {turtle.user.id})")
    print("__________________________________________________")

initial_extensions = []

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        initial_extensions.append("cogs." + filename[:-3])

if __name__ == "__main__":
    for extension in initial_extensions:
        turtle.load_extension(extension)

turtle.run(BOTTOKEN)


# Game("The Slowest Turtle Game 2")