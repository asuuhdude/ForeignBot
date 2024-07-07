import disnake
import typing
import json

from disnake.ext import commands
from disnake.ext.commands import has_permissions
from fbot import ForeignBot
from fbot.vars import VERSION

from pathlib import Path

class UtilityCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: ForeignBot = bot

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        if ctx.command.name in self.bot.config["core"]["commands"][Path(__file__).stem]["disabledCommands"]:
            raise commands.CommandInvokeError("command is disabled")

        return await super().cog_before_invoke(ctx)

    async def fetch_user_inventory(self, user_id: int) -> tuple:
        with open("./db/user_inventories.json", "r") as file:
            data = json.load(file)
        
        return (data.get(f"{user_id}").get("inventory"), data.get(f"{user_id}").get("achievements"))

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
            embed.description = "notifications have been turned **on**"
            embed.set_footer(text="swag mode: activated | this affects all servers youre in with me")
        else: 
            embed.description = "notifications have been turned **off**"
            embed.set_footer(text="literally 1984 | this affects all servers youre in with me")

        await self.bot.db.update(
            "UPDATE users SET notis = ? WHERE user_id = ?", (value, ctx.author.id)
        )


        await ctx.send(embed=embed)

    @commands.command()
    async def credits(self, ctx: commands.Context):
        embed = (
            disnake.Embed(
                colour=disnake.Colour.og_blurple(),
                title="ForeignBot Credits",
                description="[Repository](https://github.com/asuuhdude/ForeignBot)"
            )

            .set_thumbnail(url=self.bot.user.display_avatar.url)
            .set_image(url="https://cdn.discordapp.com/attachments/1046997746722295810/1255195598462783629/text.png?ex=667ee27f&is=667d90ff&hm=fc592e28e5ff5f98536b031b405f74678a7173d3f9002f325d8282d9de279635&")
            .set_footer(text=VERSION, icon_url=ctx.author.display_avatar.url)

            .add_field(name="Code Developer", value="- [asuuhdude](https://github.com/asuuhdude)")
            .add_field(name="Extra", value="- [CaedenPH](https://github.com/CaedenPH)\n- [JesterBot](https://github.com/CaedenPH/JesterBot) Contributors")
        )

        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(UtilityCommands(bot))