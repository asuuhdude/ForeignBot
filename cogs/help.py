import disnake
import typing

from disnake.ext import commands
from disnake.ext.commands import has_permissions
from fbot import ForeignBot

from pathlib import Path

class HelpCommand(commands.Cog):

    def __init__(self, bot):
        self.bot: ForeignBot = bot

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        if ctx.command.name in self.bot.config["core"]["commands"][Path(__file__).stem]["disabledCommands"]:
            raise commands.CommandInvokeError("command is disabled")

def setup(bot):
    bot.add_cog(HelpCommand(bot))