import disnake
import typing
import random

from disnake.ext import commands
from foreignbot import ForeignBot

from pathlib import Path

class FunCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: ForeignBot = bot

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        if ctx.command.name in self.bot.config["core"]["commands"][Path(__file__).stem]["disabledCommands"]:
            raise commands.CommandInvokeError("command is disabled")

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

            .set_author(name=(self.bot.config["core"]["phrases"]["commands"][ctx.command.name].get("title")).format(user=user.display_name), icon_url=user.display_avatar.url)\
            .add_field(
                name=f"**[ {'='*meter}{'  '*total} ]**",
                value=f"{user.mention} is **{percent:.0f}**% gay"
            )
        )

        if percent > 50:
            embed.set_footer(text=(self.bot.config["core"]["phrases"]["commands"][ctx.command.name].get("footerAbove")).format(user=user.display_name))
        else:
            embed.set_footer(text=(self.bot.config["core"]["phrases"]["commands"][ctx.command.name].get("footerBelow")).format(user=user.display_name))

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

            .set_author(name=(self.bot.config["core"]["phrases"]["commands"][ctx.command.name].get("title")).format(user=user.display_name), icon_url=user.display_avatar.url)\
            .add_field(
                name=f"**8{'='*meter}D**",
                value=""
            )
        )

        if meter < 25:
            embed.set_footer(text=((self.bot.config["core"]["phrases"]["commands"][ctx.command.name].get("footerBelow")).format(user=user.display_name) + f" | {meter} =\'s"))
        else:
            embed.set_footer(text=((self.bot.config["core"]["phrases"]["commands"][ctx.command.name].get("footerAbove")).format(user=user.display_name) + f" | {meter} =\'s"))

        await ctx.send(embed=embed)

    

def setup(bot):
    bot.add_cog(FunCommands(bot))