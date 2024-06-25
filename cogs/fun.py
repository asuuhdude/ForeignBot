import disnake
import typing
import random
import io

from disnake.ext import commands
from fbot import ForeignBot
from PIL import Image, ImageFilter
from glitch_this import ImageGlitcher

class FunCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: ForeignBot = bot

    @commands.command(
        aliases=[
            "hg",
            "gayhow",
            "urgay"
        ]
    )
    async def howgay(self, ctx: commands.Context, user: typing.Optional[disnake.User] = None) -> None:
        if user is None:
            user = ctx.author

        mp = 50
        meter = random.randint(0, mp)
        total = mp - meter
        
        if meter == 0:
            percent = 0
        else:
            percent = (meter / mp)*100

        embed = (
            disnake.Embed(
                colour=random.randint(0, 0xffffff),
            )

            .set_author(name=f"how gay is {user.display_name}? 🏳️‍🌈", icon_url=user.display_avatar.url)\
            .add_field(
                name=f"**[{'='*meter}{'  '*total}]**",
                value=f"{user.mention} is **{percent:.0f}**% gay"
            )
        )

        if percent > 50:
            embed.set_footer(text=f"🙄 {user.display_name} is so gay bruh")
        else:
            embed.set_footer(text=f"😶 {user.display_name} is not gay")

        await ctx.send(embed=embed)

    @commands.command(
        aliases=[
            "penissize",
            "ds",
            "penislength",
            "dicklength",
            "dl",
            "howbig",
            "hb"
        ]
    )
    async def dicksize(self, ctx: commands.Context, user: typing.Optional[disnake.User] = None) -> None:
        if user is None:
            user = ctx.author

        mp = 50
        meter = random.randint(0, mp)

        embed = (
            disnake.Embed(
                colour=random.randint(0, 0xffffff),
            )

            .set_author(name=f"how big is {user.display_name}? 🙊", icon_url=user.display_avatar.url)\
            .add_field(
                name=f"**8{'='*meter}D**",
                value=f""
            )
        )

        if meter < 25:
            embed.set_footer(text=f"🙄 {user.display_name} smh | {meter} =\'s")
        else:
            embed.set_footer(text=f"😳 {user.display_name} wsg.. | {meter} =\'s")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(FunCommands(bot))