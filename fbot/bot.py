



from __future__ import annotations

import os
import datetime
import json
import toml
import random

import colorama
import aiohttp

from disnake import (
    Activity,
    ActivityType,
    AllowedMentions,
    Intents,
    Message,
    __version__,
)

from disnake.ext.commands import Bot, when_mentioned_or, Context
from disnake.ext.tasks import loop
from colorama import Fore as f

from .db import ForeignBotDB
from .constants import VERSION, BOT_TOKEN, OWNER_IDS
from .errors import error_handler


class ForeignBot(Bot):

    def __init__(self):
        super().__init__(

            command_prefix=self.get_prefix,
            intents=Intents.all(),
            case_insensitive=True,
            strip_after_prefix=True,
            owner_ids=OWNER_IDS,
            allowed_mentions=AllowedMentions.all(),
            help_command=None

        )

        self.launch_utc = datetime.datetime.now(datetime.timezone.utc)
        self.COGS: list = list()
        self.hibernate = False

        self.loop.create_task(self.connect_database())

        colorama.init()
        print(f"{f.YELLOW}(bot.py) ForeignBot.__init__ :{f.WHITE} colorama has been initialized")

        for file in os.listdir("./cogs/"):
            if not file.startswith("_"):
                self.COGS.append(f"cogs.{file}")

    async def connect_database(self):
        self.db = await ForeignBotDB.create()  

    async def check_user_exists(self, user_id: int) -> bool:
        result = await self.db.fetchone(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
        )

        return bool(result)
    
    async def check_inventory_exists(self, user_id: int) -> bool:
        with open("./db/user_inventories.json", "r") as file:
            data = json.load(file)

        return bool(data.get(f"{user_id}"))

    async def create_user_table(self, user_id: int) -> None:
        await self.db.update(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",

            (
                user_id, # user_id
                0, # xp
                1, # level
                self.get_user(user_id).name, # name
                0, # balance
                500, # bank balance
                False # notis
            )
        )

        print(f"{f.YELLOW}(bot.py) ForeignBot.create_user_table : {f.WHITE} created user table ({user_id})({self.get_user(user_id).name}) into database")

    async def create_user_inventory(self, user_id: int) -> None:
        with open("./db/user_inventories.json", "r") as file:
            data = json.load(file)

        user_data = {
            f"{user_id}": {
                "inventory": {
                    "items": {}
                },
                "achievements": {}
            }
        }

        data.update(user_data)

        with open("./db/user_inventories.json", "w") as file:
            json.dump(data, file)

        print(f"{f.YELLOW}(bot.py) ForeignBot.create_user_inventory : {f.WHITE} created user inventory ({user_id})({self.get_user(user_id).name}) into json database")

    async def create_guild_table(self, message: Message) -> None:
        await self.db.update(
            "INSERT INTO guilds VALUES (?, ?, ?)",

            (
                message.guild.id, # guild_id
                message.guild.name, # name
                "fb$" # prefix
            )
        )

        print(f"{f.YELLOW}(bot.py) ForeignBot.create_guild_table : {f.WHITE} created guild table ({message.guild.id})({message.guild.name}) into database")

    async def find_prefix(self, guild_id: int) -> str:
        result = await self.db.fetchone(
            "SELECT prefix FROM guilds WHERE guild_id = ?", (guild_id,)
        )

        if not result:
            return "fb$"
        
        return result[0]
    
    async def insert_prefix(self, guild_id: int, prefix: str) -> None:
        result = await self.db.fetchone(
            "SELECT prefix FROM guilds WHERE guild_id = ?", (guild_id,)
        )

        if not result:
            return await self.db.update(
                "INSERT INTO guilds VALUES (?, ?)", (guild_id, prefix)
            )
        
        await self.db.update(
            "UPDATE guilds SET prefix = ? WHERE guild_id = ?", (prefix, guild_id)
        )

    async def get_prefix(self, message: Message) -> str:
        prefix = await self.find_prefix(message.guild.id)
        return when_mentioned_or(prefix)(self, message)
    
    def load_config(self) -> None:
        with open("./config.toml", "r", encoding="utf8") as file:
            self.config = toml.load(file)

    def cog_is_enabled(self, cog: str) -> bool:
        return self.config["core"]["commands"][cog].get("disableEntirely")
    
    async def process_commands(self, message: Message) -> None:
        ctx = await self.get_context(message=message, cls=Context)
        await self.invoke(ctx)
    
    def setup(self) -> None:

        print(f"{f.YELLOW}(bot.py) ForeignBot.setup : {f.WHITE} loading config.toml..")

        self.load_config()

        print(f"{f.YELLOW}(bot.py) ForeignBot.setup : {f.WHITE} loading {self.COGS}")
        loaded = []

        for file in self.COGS:
            if file.endswith("py"):
                if self.cog_is_enabled(f"{file[:-3][5:]}"):
                    print(f"{f.YELLOW}(bot.py) ForeignBot.setup : {f.WHITE} disabled {file}")
                else:
                    self.load_extension(f"{file[:-3]}")
                    loaded.append(file)

            elif self.cog_is_enabled(f"{file[5:]}"):
                print(f"{f.YELLOW}(bot.py) ForeignBot.setup : {f.WHITE} disabled {file}")

            else:
                self.load_extension(file)
                loaded.append(file)

        print(f"{f.YELLOW}(bot.py) ForeignBot.setup : {f.WHITE} loaded {f.YELLOW}{len(loaded)}{f.WHITE} cog(s)")

    @loop(seconds=600)
    async def log_data_into_db(self) -> None:
        await self.db.update(
            "INSERT INTO general_data VALUES (?, ?, ?, ?, ?, ?, ?)",

            (
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                self.latency * 1000,
                len(self.users),
                len(self.guilds),
                len([c for c in self.get_all_channels()]),
                VERSION,
                __version__
            )
        )

        print(f"{f.YELLOW}(bot.py) ForeignBot.log_data_into_db : {f.WHITE} logged data into database")

    @log_data_into_db.before_loop
    async def log_data_pre(self) -> None:
        await self.wait_until_ready()

    @loop(seconds=540)
    async def update_presence(self) -> None:
        await self.change_presence(
            activity=Activity(
                type=ActivityType.playing,
                name = random.choice(self.config["core"]["activities"]["normal"]["list"])
            )
        )

    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        guild_result = await self.db.fetchone(
            "SELECT guild_id FROM guilds WHERE guild_id = ?", (message.guild.id,)
        )

        if not await self.check_user_exists(message.author.id):
            await self.create_user_table(message.author.id)
        elif not await self.check_inventory_exists(message.author.id):
            await self.create_user_inventory(message.author.id)
        
        if not guild_result:
            await self.create_guild_table(message)

        return await super().on_message(message)
    
    async def on_command_error(self, ctx: Context, exception: Exception) -> None:
        await error_handler(ctx, exception)

    def run(self) -> None:
        print(f"{f.YELLOW}(bot.py) ForeignBot.run : {f.WHITE} starting foreignbot {f.CYAN}v{VERSION}{f.WHITE}...")

        self.setup()
        super().run(BOT_TOKEN, reconnect=True)

    async def on_ready(self) -> None:
        self.update_presence.start()
        self.log_data_into_db.start()

        print(f"{f.YELLOW}(bot.py) ForeignBot.on_ready : {f.WHITE} logged in as {f.CYAN}{self.user}{f.WHITE}")
        print(f"{f.YELLOW}(bot.py) ForeignBot.on_ready : {f.WHITE} loading took {f.YELLOW}{(datetime.datetime.now(datetime.timezone.utc) - self.launch_utc).seconds}{f.WHITE} seconds")

        self.client = aiohttp.ClientSession()

    async def close(self) -> None:
        await self.client.close()
        return await super().close()

