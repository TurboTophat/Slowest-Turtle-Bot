import nextcord
from nextcord.ext import commands

class Embeds(commands.Cog):
    def __init__(self, turtle):
        self.bot = turtle
        self._last_member = None

    @commands.command()
    async def embed(self, ctx):
        embed = nextcord.Embed(
        title="monkey",
        url="https://t3.ftcdn.net/jpg/05/55/24/96/360_F_555249604_nSnM10938DAyY0uHFZo83DaVzxEEj6lD.jpg",
        description="Just a monkey in a suit",
        colour=0x087CA7,
    )
    # embed.set_author(name="Wernerimages")
        embed.set_author(
        name=ctx.author.display_name,
        url="https://stock.adobe.com/contributor/202787442/wernerimages?load_type=author&prev_url=detail&asset_id=750983801",
        icon_url="https://cdn.icon-icons.com/icons2/2845/PNG/512/adobe_logo_icon_181321.png",
    )
        embed.set_thumbnail(
        url="https://t3.ftcdn.net/jpg/05/55/24/96/360_F_555249604_nSnM10938DAyY0uHFZo83DaVzxEEj6lD.jpg"
    )
    # inline=True Means horizontal (left and right) and inline=false means vertical (up and down)
        embed.add_field(name="test", value="test description", inline=True)
        embed.add_field(name="test2", value="test2 description", inline=True)
        embed.set_footer(text="TEXT TEXT TEXT")
        await ctx.send(embed=embed)

def setup(turtle):
    turtle.add_cog(Embeds(turtle))