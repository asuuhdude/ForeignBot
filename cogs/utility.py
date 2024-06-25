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
        result = await self.bot.db.fetchone(
            "SELECT prefix FROM guilds WHERE guild_id = ?", (ctx.guild.id,)
        )

        embed = (
            disnake.Embed(
                colour=disnake.Colour.og_blurple(),
                description=f"the current prefix is \'**{result[0]}**\'"
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
        result = await self.bot.db.fetchone(
            "SELECT prefix FROM guilds WHERE guild_id = ?", (ctx.guild.id,)
        )

        if not prefix:
            return await ctx.send(f"my guy u need a prefix i can set to\n```{result[0]}setprefix <new prefix>```")
        elif prefix == result[0]:
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
        result = await self.bot.db.fetchone(
            "SELECT prefix FROM guilds WHERE guild_id = ?", (ctx.guild.id,)
        )

        if value is None:
            return await ctx.send(f"brotha i need smth to change ur setting to\n```{result[0]}notifications <true/false>```")
        
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