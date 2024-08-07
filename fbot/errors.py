# import asyncio
import traceback
import disnake
# import json
import random

from disnake.ext.commands import (
    #BadArgument,
    CheckFailure,
    CommandInvokeError,
    CommandNotFound,
    CommandOnCooldown,
    #MemberNotFound,
    MissingPermissions,
    MissingRequiredArgument,
    #RoleNotFound,

    Context
)

#from datetime import datetime, timezone
from .constants import VERSION

async def unexpected(ctx: Context, error: Exception) -> None:
    bot = ctx.bot

    # json_file = open(f"./logs/error.json")
    # data = {
    #     "author": ctx.author.name,
    #     "id": ctx.author.id,
    #     "error": str(error),
    #     "error_dir": str(dir(error)),
    #     "command": ctx.command.name
    # }

    # json_file.write(json.dumps(data))
    phrases = [
        "that wasnt supposed to happen",
        "opps got in my code, sry",
        "fail",
        "error",
        "something went wrong"
    ]

    embed1 = (
        disnake.Embed(
            colour=disnake.Colour.red()
        )

        .set_author(name=random.choice(phrases), icon_url=bot.user.display_avatar.url)
        .add_field(
            name="important developer stuff",
            value=f"**{ctx.guild}**; **{ctx.author}**; **{ctx.command.name}**;"
        )
        .set_footer(text=VERSION)
    )

    embed2 = (
        disnake.Embed(
            colour=disnake.Colour.red(),
            description=f"{error}"
        )

        .set_footer(text=VERSION)
    )

    embed3 = (
        disnake.Embed(
            colour=disnake.Colour.red(),
            description=f"{traceback.format_exception(error, error, error.__traceback__)}"
        )

        .set_footer(text=VERSION)
    )

    await ctx.send(embeds=[embed1, embed2, embed3])

async def error_handler(ctx: Context, error: Exception) -> None:
    if ctx.bot.hibernate:
        return
    
    if isinstance(error, MissingPermissions):
        await ctx.reply("yo u dont have the permissions for that lol")
    elif isinstance(error, CheckFailure):
        pass
    elif isinstance(error, CommandNotFound):
        pass

    elif isinstance(error, MissingRequiredArgument):
        
        sig = ctx.command.signature
        command = ctx.command.name
        prefix = await ctx.bot.find_prefix(ctx.guild.id)

        if ctx.command.aliases:
            aliases = ctx.command.aliases
        else:
            aliases = []

        aliases.append(command)
        aliases = " | ".join(aliases)

        phrases = ["*buzzer sound* someone forgot an argument", "yo chief ur missing an argument", "argument missing", "uh oh u forgot an argument"]

        embed = (
            disnake.Embed(
                colour=disnake.Colour.light_gray(),
                description=f"*yo chief u forgot an argument*\n\n```{prefix}{command} {sig}``` ```command aliases: {prefix}{aliases}\n<argument> is required, [argument] is optional```"
            )

            .set_author(name=random.choice(phrases), icon_url=ctx.author.display_avatar.url)
            .set_footer(text="anything in angle brackets '<>' is required, anything in regular brackets '[]' is optional")
        )

        await ctx.send(embed=embed)

    elif isinstance(error, CommandOnCooldown):
        await ctx.reply(f"yo chief u are on cooldown for `{error.retry_after:.2f}` seconds")
    elif isinstance(error, CommandInvokeError):
        if (
            error.args[0] ==
            "Command raised an exception: Forbidden: 403 Forbidden (error code: 50013): Missing Permissions"
        ):
            await ctx.reply("im not allowed to do that, i wasnt invited with the proper permissions")
        elif (error.args[0] == "Command raised an exception: str: command is disabled"):
            return
        else:
            await unexpected(ctx, error)
    else:
        await unexpected(ctx, error)