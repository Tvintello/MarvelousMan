import discord

from config import TOKEN, PREFIX, COLOR_GREEN, DECENT
from censure import Censor  # https://github.com/Priler/samurai/tree/main/censure
from scripts.support import get_json
from random import choice
from datetime import timedelta
from scripts.timer import Timer
from scripts.role_manager import RoleManager
import asyncio

censor_ru = Censor.get(lang="ru")
phrases = get_json("scripts/phrases.json")

bad_counter = {}
user_backend_timers = {}


def reset_bad_counter(member: discord.Member):
    bad_counter[member] = 0
    print(f"RESET BAD COUNTER: {bad_counter}")


def get_profanity(text):
    info = censor_ru.clean_line(text)
    return info[3]


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = discord.Bot(intents=intents, prefix=PREFIX)

    @bot.event
    async def on_connect():
        bot.load_extension("cogs.admin")
        bot.load_extension("cogs.user")
        bot.load_extension("cogs.timer")
        await bot.sync_commands()

    @bot.event
    async def on_ready():
        global mute_role

        await RoleManager(bot).setup_role("Приличный", DECENT, COLOR_GREEN)

        for role in await bot.guilds[0].fetch_roles():
            if role.name == "Приличный":
                for member in bot.guilds[0].members:
                    await member.add_roles()

    @bot.event
    async def on_timeout(member):
        print(member)

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user:
            return

        if get_profanity(message.content):
            bad_counter[message.author] = bad_counter.setdefault(message.author, 0) + 1
            await message.channel.send(choice(phrases["on_swear"]))
            if bad_counter[message.author] >= 3:
                # await message.author.timeout_for(timedelta(minutes=5 * (bad_counter[message.author] - 2)))
                # if bad_counter[message.author] >= 12:
                #     await message.channel.send("/tenor query: гигачад")
                await message.channel.send(choice(phrases["on_mute"]))

                if user_backend_timers.get(message.author):
                    await user_backend_timers[message.author].stop()

                user_backend_timers[message.author] = Timer(timedelta(hours=(bad_counter[message.author] - 2)),
                                                                      lambda: reset_bad_counter(message.author))
                await user_backend_timers[message.author].start()
            return
        elif not message.content.startswith("/"):
            await message.channel.send(message.content)

    bot.run(TOKEN)


if __name__ == '__main__':
    run()

