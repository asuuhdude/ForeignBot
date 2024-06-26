import disnake
import typing
import random
import json

from disnake.ext import commands
from fbot import ForeignBot
from faker import Faker

class EconomyCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: ForeignBot = bot

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        if not await self.bot.check_user_exists(ctx.author.id):
            await self.bot.create_user_table(ctx.author.id)
        elif not await self.bot.check_inventory_exists(ctx.author.id):
            await self.bot.create_user_inventory(ctx.author.id)

        return await super().cog_before_invoke(ctx)
    
    async def fetch_user_inventory(self, user_id: int) -> tuple:
        with open("./db/user_inventories.json", "r") as file:
            data = json.load(file)
        
        return (data.get(f"{user_id}").get("inventory"), data.get(f"{user_id}").get("achievements"))

    @commands.command(
        aliases=[
            "bal",
            "b",
            "brokeahh"
        ]
    )
    async def balance(self, ctx: commands.Context, user: typing.Optional[disnake.User] = None) -> None:
        if user is None:
            user = ctx.author
        elif user.bot:
            return await ctx.send("dude r u stupid? bots r too rich for banks lmao")

        bal = await self.bot.db.fetchone(
            "SELECT balance FROM users WHERE user_id = ?", (user.id,)
        )
        bal = bal[0]

        bank = await self.bot.db.fetchone(
            "SELECT bank FROM users WHERE user_id = ?", (user.id,)
        )
        bank = bank[0]

        embed = (
            disnake.Embed(
                colour=disnake.Colour.green(),
                description=f"on hand: **{bal:.2f}** FC$\nin bank: **{bank:.2f}** FC$"
            )

            .set_author(name=f"{user.name}'s balance 💸", icon_url=user.display_avatar.url)
            .set_footer(text=f"powered by ur crippling dept", icon_url=ctx.author.display_avatar.url)
        )

        if bal < 1 and bank < 1000:
            embed.description = f"on hand: **{bal:.0f}** FC$\nin bank: **{bank:.0f}** FC$\n\n*....brotha ur broke LMAO*"
        if user == ctx.author:
            embed.set_author(name=f"{user.name}'s balance 💸")

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def beg(self, ctx: commands.Context) -> None:
        faker = Faker()
        accepted_responses = ["oh you poor thing", "sure lol", "here, take my money", "yea i gotchu", "no problem"]
        denied_responses = ["lol no", "what a waste of FC$", "no????", "nah, not today", "man fuck you and your dog ass", "stop begging"]

        amount = random.randint(1, 100)
        chance = random.randint(0, 4)

        embed1 = (
            disnake.Embed()

            .set_author(name=faker.name())
        )

        embed2 = (
            disnake.Embed(
                colour=disnake.Colour.yellow()
            )

            .set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        )

        if chance > 2:
            embed1.description = random.choice(accepted_responses)
            embed1.colour = disnake.Colour.green()

            embed2.description = f":money_with_wings: you begged and got **{amount}** FC$"

            await self.bot.db.update(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, ctx.author.id)
            )

        else:
            embed1.description = random.choice(denied_responses)
            embed1.colour = disnake.Colour.red()

            embed2.description = f":money_with_wings: you begged and got nothing smh"

        await ctx.send(embeds=[embed1, embed2])

    @commands.command()
    @commands.cooldown(1, 21, commands.BucketType.guild)
    async def rob(self, ctx: commands.Context, user: typing.Optional[disnake.User] = None) -> None:
        # this arg handling is so bad
        if user is None:
            return await ctx.send("who...who r u robbing?")
        elif user == self.bot.user:
            return await ctx.reply("u cant rob me lmao")
        elif user.bot:
            return await ctx.send("bro bots have norton antivirus installed, they cant b robbed..")
        elif user == ctx.author:
            return await ctx.send("u cant rob urself lmao")
        
        if not await self.bot.check_user_exists(user.id):
            await self.bot.create_user_table(user.id)

        embed_failure = (
            disnake.Embed(
                colour=disnake.Colour.red()
            )

            .set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        )

        target_bal = await self.bot.db.fetchone(
            "SELECT balance FROM users WHERE user_id = ?", (user.id,)
        )
        target_bal = target_bal[0]

        recip_bal = await self.bot.db.fetchone(
            "SELECT balance FROM users WHERE user_id = ?", (ctx.author.id,)
        )
        recip_bal = recip_bal[0]

        if recip_bal < 1000:
            embed_failure.description = ":x: sry ur too poor to rob someone...\n`min.: 1000 FC$`"
            return await ctx.send(embed=embed_failure)

        if target_bal < 1000:
            embed_failure.description = ":x: bro is u srsly tryna rob someone wit pennies??\n`min.: 1000 FC$`"
            return await ctx.send(embed=embed_failure)
        
        amount = round(target_bal / (random.randint(1, 25) % target_bal))
        
        if await self.fetch_user_inventory(user.id)[0]["items"].get("scary_mask"):
            chance = random.randint(0, 10)
        else:
            chance = random.randint(0, 5)
        
        embed_success = (
            disnake.Embed(
                colour=disnake.Colour.green(),
                description=f":money_with_wings: yoo you robbed {user.mention} for **{amount:.0f}** FC$"
            )

            .set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        )

        if chance < 3:
            await self.bot.db.update(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user.id)
            )

            await self.bot.db.update(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, ctx.author.id)
            )

            await ctx.send(embed=embed_success)
        else:
            await self.bot.db.update(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?", (500, ctx.author.id)
            )

            embed_failure.description = f":x: dude u had the bag and then u slipped up wth!!\n`lost 500 FC$`"
            await ctx.send(embed=embed_failure)

    @commands.command()
    async def shop(self, ctx: commands.Context, option: typing.Optional[str] = None, item: str = None, amount: int = 1) -> None:
        with open("./resources/shop.json", "r") as file:
            shop_data = json.load(file)

        if option is None:
            return await ctx.send(f"bro that command needs more arguments..\n```{await self.bot.find_prefix(ctx.guild.id)}shop <info/buy/list> <item> <amount>```")
        elif option.lower() == "list":
            embed = (
                disnake.Embed(
                    colour=disnake.Colour.og_blurple(),
                )

                .set_author(name="foreignbot shop", icon_url=ctx.author.display_avatar.url)
                .set_footer(text=ctx.author.display_name)
            )

            for item in shop_data["shop"]["items"]:
                embed.add_field(
                    name=f"{shop_data['shop']['items'][item]['icon']} {shop_data['shop']['items'][item]['displayName']}",
                    value=f"**{shop_data['shop']['items'][item]['price']}** FC$\n\n*{shop_data['shop']['items'][item]['description']}*",
                )

            await ctx.send(embed=embed)

        elif option.lower() == "buy":
            if item is None:
                return await ctx.reply(f"haha im gonna buy nothing its gonna b so funny\n```available items: {', '.join(shop_data['shop']['items'].keys())}```")

            if item not in shop_data["shop"]["items"]:
                return await ctx.send(f"that item does not exist\n```available items: {', '.join(shop_data['shop']['items'].keys())}```")
            
            bal = await self.bot.db.fetchone(
                "SELECT balance FROM users WHERE user_id = ?", (ctx.author.id,)
            )
            bal = bal[0]
            price = (shop_data["shop"]["items"][item]["price"] * amount)

            with open("./db/user_inventories.json", "r") as file:
                commit_data = json.load(file)

            if price > bal:
                return await ctx.send("ur broke ass cant afford that item")
            
            await self.bot.db.update(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?", (price, ctx.author.id)
            )

            user_data, user_achv = await self.fetch_user_inventory(ctx.author.id)

            if user_data["items"].get(item) is None:
                commit_data[f"{ctx.author.id}"]["inventory"]["items"][item] = amount
            else: commit_data[f"{ctx.author.id}"]["inventory"]["items"][item] += amount

            notifications = await self.bot.db.fetchone(
                "SELECT notis FROM users WHERE user_id = ?", (ctx.author.id,))
            notifications = bool(notifications[0])

            with open("./db/user_inventories.json", "w") as file:
                user_data = json.dump(commit_data, file)
            user_data, user_achv = await self.fetch_user_inventory(ctx.author.id)

            if user_data["items"].get("scary_mask") is not None and user_data["items"].get("scary_mask") >= 25 and not user_achv.get("achievement_mentlegen"):
                commit_data[f"{ctx.author.id}"]["achievements"]["achievement_mentlegen"] = True

                with open("./resources/achievements.json", "r") as file:
                    achievements = json.load(file)

                embed = (
                    disnake.Embed(
                        colour=disnake.Colour.yellow(),
                        description=achievements["achievements"]["achievement_mentlegen"]["description"],
                        title=achievements["achievements"]["achievement_mentlegen"]["displayName"]
                    )

                    .set_author(name="Achievement Obtained!", icon_url=ctx.author.display_avatar.url)
                    .set_thumbnail(url=achievements["achievements"]["achievement_mentlegen"]["display"])
                )

                if notifications == True:
                    await ctx.send(embed=embed)
                await self.bot.db.update(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?", (int(achievements["achievements"]["achievement_mentlegen"]["reward"]), ctx.author.id)
                )

            elif user_data["items"].get("inf_money_glitch") is not None and user_data["items"].get("inf_money_glitch") >= 1 and not user_achv.get("achievement_were_rich"):
                commit_data[f"{ctx.author.id}"]["achievements"]["achievement_were_rich"] = True

                with open("./resources/achievements.json", "r") as file:
                    achievements = json.load(file)

                embed = (
                    disnake.Embed(
                        colour=disnake.Colour.yellow(),
                        description=achievements["achievements"]["achievement_were_rich"]["description"],
                        title=achievements["achievements"]["achievement_were_rich"]["displayName"]
                    )

                    .set_author(name="Achievement Obtained!", icon_url=ctx.author.display_avatar.url)
                    .set_thumbnail(url=achievements["achievements"]["achievement_were_rich"]["display"])
                )

                if notifications == True:
                    await ctx.send(embed=embed)
                commit_data[f"{ctx.author.id}"]["inventory"]["items"]["hidden_codex"] = 1

            with open("./db/user_inventories.json", "w") as file:
                user_data = json.dump(commit_data, file)
                file.close()

            embed = (
                disnake.Embed(
                    colour=disnake.Colour.green(),
                    description=f":money_with_wings: bought `x{amount}` {shop_data['shop']['items'][item]['icon']} `{shop_data['shop']['items'][item]['displayName']}` for **{(shop_data['shop']['items'][item]['price']*amount)}** FC$"
                )
            )

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(EconomyCommands(bot))