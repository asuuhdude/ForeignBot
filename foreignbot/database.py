

from __future__ import annotations


import aiosqlite
import typing

class ForeignBotDB:
    
    def __init__(self):
        self.db: aiosqlite.Connection

    @classmethod
    async def create(cls: typing.Type[ForeignBotDB]) -> ForeignBotDB:
        self = cls()
        self.db = await aiosqlite.connect("./database/fbot.db")

        with open("./foreignbot/utils/schema.sql") as schema:
            await self.db.executescript(schema.read())

        return self
    
    async def execute(self, query: str, *args: typing.Any) -> aiosqlite.Cursor:
        async with self.db.cursor() as cur:
            return await cur.execute(query, *args)
        
    async def update(self, query: str, *args: typing.Any) -> aiosqlite.Cursor:
        async with self.db.cursor() as cur:
            resp = await cur.execute(query, *args)
            await self.db.commit()
            return resp
        
    async def fetchone(self, query: str, *args: typing.Any) -> typing.Tuple:
        async with self.db.cursor() as cur:
            return await (await cur.execute(query, *args)).fetchone()
        
    async def fetchall(self, query: str, *args: typing.Any) -> typing.Tuple:
        async with self.db.cursor() as cur:
            return await (await cur.execute(query, *args)).fetchall()