import discord

from config import TOKEN, PREFIX, COLOR_RED
from censure import Censor
from scripts.support import get_json
from random import choice
import asyncio

censor_ru = Censor.get(lang="ru")
phrases = get_json("scripts/phrases.json")
mute_role = discord.abc.Snowflake

bad_counter = {}
say_counter = {}


def get_profanity(text):
    info = censor_ru.clean_line(text)
    return info[3]


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = discord.Bot(intents=intents)

    async def setup_role(role_name):
        exists = False
        for role in await bot.guilds[0].fetch_roles():
            if role.name == role_name:
                exists = True
                break
        if exists:
            return

        permissions = discord.Permissions.none()
        permissions.update(view_channel=True)
        await bot.guilds[0].create_role(
            name=role_name,
            color=COLOR_RED,
            hoist=True,
            permissions=permissions
        )

    async def set_timer(ctx, timeInput):
        try:
            time = int(timeInput)
        except:
            convertTimeList = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'S': 1, 'M': 60, 'H': 3600, 'D': 86400}
            time = int(timeInput[:-1]) * convertTimeList[timeInput[-1]]
        if time > 86400:
            await ctx.send("I can\'t do timers over a day long")
            return
        if time <= 0:
            await ctx.send("Timers don\'t go into negatives :/")
            return
        if time >= 3600:
            message = await ctx.send(f"Timer: {time // 3600} hours {time % 3600 // 60} minutes {time % 60} seconds")
        elif time >= 60:
            message = await ctx.send(f"Timer: {time // 60} minutes {time % 60} seconds")
        elif time < 60:
            message = await ctx.send(f"Timer: {time} seconds")
        while True:
            try:
                await asyncio.sleep(5)
                time -= 5
                if time >= 3600:
                    await message.edit(
                        content=f"Timer: {time // 3600} hours {time % 3600 // 60} minutes {time % 60} seconds")
                elif time >= 60:
                    await message.edit(content=f"Timer: {time // 60} minutes {time % 60} seconds")
                elif time < 60:
                    await message.edit(content=f"Timer: {time} seconds")
                if time <= 0:
                    await message.edit(content="Ended!")
                    await ctx.send(f"{ctx.author.mention} Your countdown Has ended!")
                    break
            except:
                break

    @bot.event
    async def on_ready():
        global mute_role
        await setup_role("Замученный")
        for role in await bot.guilds[0].fetch_roles():
            if role.name == "Замученный":
                mute_role = role
                break

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user:
            return

        if get_profanity(message.content):
            bad_counter[message.author] = bad_counter.setdefault(message.author, 0) + 1
            await message.channel.send(choice(phrases["on_swear"]))
            if bad_counter[message.author] >= 3:
                await message.author.add_roles(mute_role)
                await message.channel.send(choice(phrases["on_mute"]))
            return
        elif not message.content.startswith("/"):
            await message.channel.send(message.content)

    @bot.command()
    async def say(ctx, message):
        await ctx.respond(message)

    @bot.command()
    async def get_avatar(ctx: discord.commands.context.ApplicationContext, user_name: str = ""):
        if user_name:
            for user in bot.get_all_members():
                if user.name.lower() == user_name.lower():
                    await ctx.respond(user.avatar)
                    break
            else:
                if ctx.message.author.name.lower() == user_name.lower():
                    await ctx.respond(ctx.user.avatar)
        else:
            await ctx.respond(ctx.user.avatar)

    bot.run(TOKEN)


if __name__ == '__main__':
    run()

