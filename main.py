import discord

from config import TOKEN, PREFIX, COLOR_RED, COLOR_GREEN
from censure import Censor  # https://github.com/Priler/samurai/tree/main/censure
from scripts.support import get_json
from random import choice
from typing import Callable
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
    bot = discord.Bot(intents=intents, prefix=PREFIX)

    async def setup_role(role_name, permissions, color):
        exists = False
        for role in await bot.guilds[0].fetch_roles():
            if role.name == role_name:
                exists = True
                break
        if exists:
            return

        await bot.guilds[0].create_role(
            name=role_name,
            color=color,
            hoist=True,
            permissions=permissions
        )

    async def set_timer(ctx, time_input, func: Callable):
        try:
            time = int(time_input)
        except ValueError:
            convert_time_list = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'S': 1, 'M': 60, 'H': 3600, 'D': 86400}
            time = int(time_input[:-1]) * convert_time_list[time_input[-1]]
        while True:
            try:
                await asyncio.sleep(5)
                time -= 5
                if time <= 0:
                    await func()
                    await ctx.send(f"{ctx.author.mention} Твой срок истек, теперь ты можешь опять засорять нам чат!")
                    await ctx.respond(choice(phrases["on_mute_end"]))
                    break
            except Exception:
                break

    @bot.command()
    async def set_timer(ctx, time_input, end_message: str = "Таймер истек!"):

        # TODO: таймер в отдельный класс, чтобы каждый участник мог ставить свой таймер и останавливать его

        try:
            try:
                time = int(time_input)
            except ValueError:
                convert_time_list = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'S': 1, 'M': 60, 'H': 3600, 'D': 86400}
                time = int(time_input[:-1]) * convert_time_list[time_input[-1]]
            if time > 86400:
                await ctx.respond("Я не могу считать дольше чем 24 часа, пожалей меня, "
                                  "попробуй так же 100 тысяч секунд считать, посмотрим на тебя после этого")
                return
            if time <= 0:
                await ctx.respond("Время не может быть отрицательным. Тебя этому в школе не учили что ли?")
                return
            if time >= 3600:
                message = await ctx.respond(f"Таймер: {time // 3600} часов {time % 3600 // 60} минут {time % 60} секунд")
            elif time >= 60:
                message = await ctx.respond(f"Таймер: {time // 60} минут {time % 60} секунд")
            else:
                message = await ctx.respond(f"Таймер: {time} секунд")
            while True:
                try:
                    await asyncio.sleep(5)
                    time -= 5
                    if time >= 3600:
                        await message.edit(
                            content=f"Таймер: {time // 3600} часов {time % 3600 // 60} минут {time % 60} секунд")
                    elif time >= 60:
                        await message.edit(content=f"Таймер: {time // 60} минут {time % 60} секунд")
                    elif time < 60:
                        await message.edit(content=f"Таймер: {time} секунд")
                    if time <= 0:
                        await message.edit(content=f"{ctx.author.mention} {end_message}")
                        break
                except Exception:
                    break
        except ValueError:
            await ctx.respond(f"Че это вообще такое **{time_input}**, формулируй нормально, я ничего не понял")

    @bot.event
    async def on_connect():
        bot.load_extension("cogs.admin_cog")
        await bot.sync_commands()

    @bot.event
    async def on_ready():
        global mute_role

        muted = discord.Permissions.none()
        muted.update(view_channel=True)
        await setup_role("Замученный", muted, COLOR_RED)
        unmuted = discord.Permissions.general()
        await setup_role("Приличный", unmuted, COLOR_GREEN)

        for role in await bot.guilds[0].fetch_roles():
            if role.name == "Замученный":
                mute_role = role
            elif role.name == "Приличный":
                for member in bot.guilds[0].members:
                    await member.add_roles()

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user:
            return

        if get_profanity(message.content):
            bad_counter[message.author] = bad_counter.setdefault(message.author, 0) + 1
            await message.channel.send(choice(phrases["on_swear"]))
            if bad_counter[message.author] >= 3:
                for role in message.author.roles:
                    if not role.name == "@everyone":
                        await message.author.remove_roles(role)

                await message.author.add_roles(mute_role)
                await message.channel.send(choice(phrases["on_mute"]))
            return
        elif not message.content.startswith("/"):
            await message.channel.send(message.content)

    @bot.command()
    async def say(ctx: discord.commands.context.ApplicationContext, message):
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

