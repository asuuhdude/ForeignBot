import disnake
import typing
import json

from disnake.ext import commands
from disnake.ext.commands import has_permissions
from fbot import ForeignBot
from fbot.vars import VERSION

class UtilityCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: ForeignBot = bot

    @commands.command()
    async def prefix(self, ctx: commands.Context) -> None:
        embed = (
            disnake.Embed(
                colour=disnake.Colour.og_blurple(),
                description=f"the current prefix is \'**{await self.bot.find_prefix(ctx.guild.id)}**\'"
            )
        )

        await ctx.send(embed=embed)

    @has_permissions(administrator=True)
    @commands.command(
        aliases=[
            "set_prefix"
        ]
    )
    async def setprefix(self, ctx: commands.Context, *, prefix: typing.Optional[str]) -> None:
        if not prefix:
            return await ctx.send(f"my guy u need a prefix i can set to\n```{await self.bot.find_prefix(ctx.guild.id)}setprefix <new prefix>```")
        elif prefix == await self.bot.find_prefix(ctx.guild.id):
            return await ctx.send("uhhh dude u already have that prefix")
        elif prefix == "reset":
            prefix = "fb$"

        await self.bot.insert_prefix(ctx.guild.id, prefix)

        embed = (
            disnake.Embed(
                colour=disnake.Colour.green(),
                description=f"prefix has been set to \'**{prefix}**\'"
            )
        )

        await ctx.send(embed=embed)
    
    @commands.command(
        aliases=[
            "notis",
            "set_notis",
            "setnotis"
        ]
    )
    async def notifications(self, ctx: commands.Context, value: typing.Optional[bool] = None) -> None:
        if not await self.bot.check_user_exists(ctx.author.id):
            await self.bot.create_user_table(ctx.author.id)

        if value is None:
            return await ctx.send(f"brotha i need smth to change ur setting to\n```{await self.bot.find_prefix(ctx.guild.id)}notifications <true/false>```")
        
        embed = (
            disnake.Embed(
                colour=disnake.Colour.green(),
            )
        )

        if value: 
            embed.description = f"notifications have been turned **on**"
        else: 
            embed.description = f"notifications have been turned **off**"

        await self.bot.db.update(
            "UPDATE users SET notis = ? WHERE user_id = ?", (value, ctx.author.id)
        )


        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(UtilityCommands(bot))