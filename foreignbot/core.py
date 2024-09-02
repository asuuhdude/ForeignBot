# -------------------------------------- //
# 
# 
#
# uhhhh pretend i put stuff here
# TODO
#
#
# -------------------------------------- //

from __future__ import annotations

import os
import datetime
import json
# import toml
import random
import yaml

import colorama
import aiohttp
import aioshutil

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

from pathlib import Path

from .database import ForeignBotDB
from .constants import VERSION, BOT_TOKEN, OWNER_IDS, CONTRIBUTOR_IDS
from .errorhandler import error_handler


class ForeignBot(Bot):

    def __init__(self):
        super().__init__(

            command_prefix=self.get_prefix,
            intents=Intents.all(),
            case_insensitive=True,
            strip_after_prefix=True,
            owner_ids=list(map(int, OWNER_IDS.replace("[", "").replace("]", "").split(","))),
            allowed_mentions=AllowedMentions.all(),
            help_command=None

        )

        self.launch_utc = datetime.datetime.now(datetime.timezone.utc)
        self.COGS: list = list()
        self.hibernate = False

        self.loop.create_task(self.connect_database())

        colorama.init()
        print(f"{f.YELLOW}(core.py) ForeignBot.__init__ :{f.WHITE} colorama has been initialized")

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

        # as of v2.0.0-prototype, the file hierarchy has been changed -
        # -to be nicer on the eyes. subsequently, this function previously -
        # -always assumed that user_inventories.json already existed, which it did not when the hierarchy was changed. oops
        #
        # using the "a+" mode, python will automatically create the file if it does not exist..
        if not os.path.exists("./database/user_inventories.json"):
            open("./database/user_inventories.json", "a+").write("{}") # ..and then write("{}") because json gets very upset about an empty file

        with open("./database/user_inventories.json", "r") as file:
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

        print(f"{f.YELLOW}(core.py) ForeignBot.create_user_table : {f.WHITE} created user table ({user_id})({self.get_user(user_id).name}) into database")

    async def create_user_inventory(self, user_id: int) -> None:
        with open("./database/user_inventories.json", "r") as file:
            data = json.load(file)

        # OK, i know this looks like a lot and is pretty ugly
        # but os.environ does not respect types when loading from a .env file
        # so i have to do this..
        if user_id in list(map(int, CONTRIBUTOR_IDS.replace("[", "").replace("]", "").split(","))): # used for rewarding bug reporters with the finders fee
            user_data = {
                f"{user_id}": {
                    "inventory": {
                        "items": {
                            "finders_fee": 1
                        }
                    },
                    "achievements": {}
                }
            }
        else:
            user_data = {
                f"{user_id}": {
                    "inventory": {
                        "items": {}
                    },
                    "achievements": {}
                }
            }

        data.update(user_data)

        with open("./database/user_inventories.json", "w") as file:
            json.dump(data, file)

        print(f"{f.YELLOW}(core.py) ForeignBot.create_user_inventory : {f.WHITE} created user inventory ({user_id})({self.get_user(user_id).name}) into json database")

    async def create_guild_table(self, message: Message) -> None:
        with open("./config.yaml", "r", encoding="utf8") as file:
            prefix = yaml.safe_load(file).get("core").get("commandPrefix")

        await self.db.update(
            "INSERT INTO guilds VALUES (?, ?, ?)",

            (
                message.guild.id, # guild_id
                message.guild.name, # name
                prefix # prefix
            )
        )

        print(f"{f.YELLOW}(core.py) ForeignBot.create_guild_table : {f.WHITE} created guild table ({message.guild.id})({message.guild.name}) into database")

    async def find_prefix(self, guild_id: int) -> str:
        result = await self.db.fetchone(
            "SELECT prefix FROM guilds WHERE guild_id = ?", (guild_id,)
        )

        # useless ??
        if not result:
            with open("./config.yaml", "r", encoding="utf8") as file:
                return yaml.safe_load(file).get("core").get("commandPrefix")
        
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
        with open("./config.yaml", "r", encoding="utf8") as file:
            self.config = yaml.safe_load(file)

    def cog_is_enabled(self, cog: str) -> bool:
        return self.config["core"]["commands"][cog].get("disableEntirely")
    
    async def process_commands(self, message: Message) -> None:
        ctx = await self.get_context(message=message, cls=Context)
        await self.invoke(ctx)
    
    def setup(self) -> None:

        print(f"{f.YELLOW}(core.py) ForeignBot.setup : {f.WHITE} loading config.yaml..")

        self.load_config()

        print(f"{f.YELLOW}(core.py) ForeignBot.setup : {f.WHITE} loading {self.COGS}")
        loaded = []

        for file in self.COGS:
            if file.endswith("py"):
                if self.cog_is_enabled(f"{file[:-3][5:]}"):
                    print(f"{f.YELLOW}(core.py) ForeignBot.setup : {f.WHITE} disabled {file}")
                else:
                    self.load_extension(f"{file[:-3]}")
                    loaded.append(file)

            elif self.cog_is_enabled(f"{file[5:]}"):
                print(f"{f.YELLOW}(core.py) ForeignBot.setup : {f.WHITE} disabled {file}")

            else:
                self.load_extension(file)
                loaded.append(file)

        print(f"{f.YELLOW}(core.py) ForeignBot.setup : {f.WHITE} loaded {f.YELLOW}{len(loaded)}{f.WHITE} cog(s)")

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

        print(f"{f.YELLOW}(core.py) ForeignBot.log_data_into_db : {f.WHITE} logged data into database")

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

    async def check_size_of_logs(self) -> None:
        log_dir = Path("./logs/")
        size = sum(file.stat().st_size for file in log_dir.glob("**/*") if file.is_file())

        if size > 31000:
            if self.config["core"].get("purgeLogs"):
                print(f"{f.YELLOW}(core.py) ForeignBot.check_size_of_logs : {f.WHITE} log dir exceeds 31000 bytes, purging logs")
                aioshutil.rmtree(log_dir)

            else:
                # okay, this is sorta the worst thing ever

                print(f"{f.YELLOW}(core.py) ForeignBot.check_size_of_logs : {f.WHITE} log dir exceeds 31000 bytes, archiving logs")
                print(f"{f.YELLOW}(core.py) ForeignBot.check_size_of_logs : {f.WHITE} to disable logging archiving, set {f.CYAN}'purgeLogs'{f.WHITE} to {f.YELLOW}'true'{f.WHITE} in config.yaml")
                
                filename = f"logs-{(datetime.datetime.now(datetime.timezone.utc)).date()}"

                # we dont want to compress the files that are already compressed
                # we arent doing inception levels of compression here
                moved_archives = []
                for file in os.listdir(log_dir):
                    if file.endswith(".bz2") or file.endswith(".zip") or file.endswith(".tar"):
                        await aioshutil.move(src=Path(f"./logs/{file}"), dst=Path("./"))
                        moved_archives.append(file)

                if self.config["core"].get("favoredLogCompressionFormat") == "tar.bz2":
                    await aioshutil.make_archive(base_name=filename, root_dir=log_dir, format="bztar")
                else:
                    await aioshutil.make_archive(base_name=filename, root_dir=log_dir, format=self.config["core"].get("favoredLogCompressionFormat"))

                # move previously compressed archives back into the log dir
                for item in moved_archives:
                    await aioshutil.move(src=Path(f"./{item}"), dst=log_dir) 
                
                # purge all uncompressed logs
                for file in os.listdir(log_dir):
                    if file.endswith(".json"):
                        os.remove(os.path.join(log_dir, file)) # is this asynchronous? prolly not..

                # for some reason, we need to move the compressed log back into the log dir, shouldnt be necessary............why
                await aioshutil.move(src=Path(f"{filename}.{self.config['core'].get('favoredLogCompressionFormat')}"), dst=log_dir)

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
        print(f"{f.YELLOW}(core.py) ForeignBot.run : {f.WHITE} starting foreignbot {f.CYAN}v{VERSION}{f.WHITE}...")

        self.setup()
        super().run(BOT_TOKEN, reconnect=True)

    async def on_ready(self) -> None:
        self.update_presence.start()
        self.log_data_into_db.start()

        await self.check_size_of_logs()

        print(f"{f.YELLOW}(core.py) ForeignBot.on_ready : {f.WHITE} logged in as {f.CYAN}{self.user}{f.WHITE}")
        print(f"{f.YELLOW}(core.py) ForeignBot.on_ready : {f.WHITE} loading took {f.YELLOW}{(datetime.datetime.now(datetime.timezone.utc) - self.launch_utc).seconds}{f.WHITE} seconds")

        self.client = aiohttp.ClientSession()

    async def close(self) -> None:
        await self.client.close()
        return await super().close()

