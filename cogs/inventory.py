import disnake
# import typing
import asyncio
import aiofiles
import os

from disnake.ext import commands
from foreignbot import ForeignBot

from pathlib import Path

class InventoryCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: ForeignBot = bot
        self.lua = self.bot.lua_runtime

        # TODO
        # send_image
        # send_video
        # access database/inventories
        self.dispatcher = {
            "send_message": lambda ctx, content: self.send_message(ctx, content),
            "send_embed": lambda ctx, title, description, color=None: self.send_embed(ctx, title, description, color)
        }
        self.item_registry = {}

        self.lua.globals().disnake_dispatcher = self.dispatcher
        self.lua.execute("""
            function call_disnake_func(func_name, ctx, ...)
                disnake_dispatcher[func_name](ctx, ...)
            end
                         
            function send_message(ctx, content)
                call_disnake_func('send_message', ctx, content)
            end
                         
            function send_embed(ctx, title, description, color)
                call_disnake_func('send_embed', ctx, title, description, color)
            end
        """)

    async def load_lua_script(self, file):
        async with aiofiles.open(file, "r") as f:
            content = await f.read()
            self.lua.execute(content)

    async def load_lua_directory(self, dir):
        tasks = [self.load_lua_script(os.path.join(dir, file)) for file in os.listdir(dir) if file.endswith(".lua")]
        await asyncio.gather(*tasks)

    async def lua_function_registrar(self, file):
        func = os.path.splitext(os.path.basename(file))[0]
        lua_func = self.lua.globals()[func]

        self.item_registry[func] = lua_func

    async def register_lua_funcs(self, dir):
        tasks = [self.lua_function_registrar(os.path.join(dir, file)) for file in os.listdir(dir) if file.endswith(".lua")]
        await asyncio.gather(*tasks)

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        if ctx.command.name in self.bot.config["core"]["commands"][Path(__file__).stem]["disabledCommands"]:
            raise commands.CommandInvokeError("command is disabled")
        
        await self.load_lua_directory("items")
        await self.register_lua_funcs("items")
        
    def send_message(self, ctx: commands.Context, content: str) -> None:
        self.bot.loop.create_task(ctx.send(content))
    
    def send_embed(self, ctx: commands.Context, title: str, description: str, color = None) -> None:
        embed =  disnake.Embed(title=title, description=description, colour=1212 if color is None else color)
        self.bot.loop.create_task(ctx.send(embed=embed))

    @commands.command()
    async def item(self, ctx: commands.Context, name: str, *args) -> None:
        if name in self.item_registry:
            func = self.item_registry[name]
            func(ctx, *args)

def setup(bot):
    bot.add_cog(InventoryCommands(bot))