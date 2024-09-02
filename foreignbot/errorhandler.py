import traceback
import disnake
import random
import json
import yaml

from datetime import datetime, timezone, timedelta
from calendar import timegm
from disnake.ext.commands import (
    BadArgument,
    CheckFailure,
    CommandInvokeError,
    CommandNotFound,
    CommandOnCooldown,
    MemberNotFound,
    UserNotFound,
    MissingPermissions,
    MissingRequiredArgument,
    BadLiteralArgument,
    #RoleNotFound,

    Context
)

from .constants import VERSION

with open("./config.yaml", "r", encoding="utf8") as file:
    config = yaml.safe_load(file)

async def unexpected(ctx: Context, error: Exception) -> None:
    time = datetime.now(timezone.utc)

    with open(f"./logs/{time.date()}_{time.hour}.{time.minute}.{time.second}.{time.microsecond}.json", "a+") as json_file:
        data = {
            "author": ctx.author.name,
            "id": ctx.author.id,
            "error": str(error),
            "error_dir": str(dir(error)),
            "command": ctx.command.name
        }

        json_file.write(json.dumps(data))
        
    phrases = config["core"]["phrases"]["onCommandError"]["unexpectedError"]

    embed1 = (
        disnake.Embed(
            colour=disnake.Colour.red()
        )

        .set_author(name=random.choice(phrases))
        .add_field(
            name="important developer stuff:",
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

    elif isinstance(error, MissingRequiredArgument) or isinstance(error, BadArgument) or isinstance(error, BadLiteralArgument):
        # TODO, MAKE OPTIONAL AND REQUIRED ARGS DYNAMICALLY COLORED
        sig = ctx.command.signature
        command = ctx.command.name
        prefix = await ctx.bot.find_prefix(ctx.guild.id)

        if ctx.command.aliases:
            aliases = ctx.command.aliases
        else:
            aliases = []

        aliases.append(command)
        aliases = " | ".join(aliases)

        phrases = ctx.bot.config["core"]["phrases"]["onCommandError"]["invalidOrMissingArgument"]

        # make this easier on the eyes
        embed = (
            disnake.Embed(
                colour=disnake.Colour.light_gray(),
                description=f"*yo chief u forgot an argument*\n\n```ansi\n\u001b[1;37m{prefix}\u001b[36m{command}\u001b[0m \u001b[0;33m{sig}``` ```ansi\ncommand aliases: \u001b[1;37m{prefix}{aliases}\u001b[0m\n\u001b[1;37m<argument>\u001b[0m is \u001b[4;31mrequired\u001b[0m, \u001b[1;37m[argument]\u001b[0m is \u001b[4;32moptional\u001b[0m```"
            )

            .set_author(name=random.choice(phrases), icon_url=ctx.author.display_avatar.url)
            .set_footer(text="anything in angled brackets '<>' is required, anything in regular brackets '[]' is optional")
        )

        await ctx.send(embed=embed)

    elif isinstance(error, CommandOnCooldown):

        phrases = ctx.bot.config["core"]["phrases"]["onCommandError"]["onCommandCooldown"]

        # another v2.0.0-prototype update, made this really ugly one liner
        # JUST FOR UNIX TIME, WHY IT GOTTA BE THIS UGLY???? a whopping 2 libraries used to do this
        unix_timestamp = timegm((datetime.now(timezone.utc) + timedelta(seconds=error.retry_after)).utctimetuple())

        embed = (
            disnake.Embed(
                colour=disnake.Colour.light_gray(),
                description=f"this command can be used again <t:{unix_timestamp:.0f}:R>"
            )

            .set_author(name=random.choice(phrases))
            .set_footer(text=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        )

        await ctx.send(embed=embed)
    elif isinstance(error, MemberNotFound) or isinstance(error, UserNotFound):
        embed = (
            disnake.Embed(
                colour=disnake.Colour.red(),
                description=":no_entry_sign: i couldnt find that user"
            )
        )

        return await ctx.send(embed=embed)
    elif isinstance(error, CommandInvokeError):
        if (
            error.args[0] ==
            "Command raised an exception: Forbidden: 403 Forbidden (error code: 50013): Missing Permissions"
        ):
            await ctx.reply(config["core"]["phrases"]["onCommandError"].get("missingPermissions"))
        elif (error.args[0] == "Command raised an exception: str: command is disabled"):

            if config["core"].get("informUsersAboutCommandAvailability"):
                return await ctx.reply(config["core"]["phrases"]["onCommandError"].get("onDisabledCommand"))
                
            else:
                return
        else:
            await unexpected(ctx, error)
    else:
        await unexpected(ctx, error)