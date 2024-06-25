import disnake
import typing

from disnake.ext import commands
from disnake.ext.commands import has_permissions
from fbot import ForeignBot

class HelpCommand(commands.Cog):

    def __init__(self, bot):
        self.bot: ForeignBot = bot

def setup(bot):
    bot.add_cog(HelpCommand(bot))