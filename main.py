import discord

from config import (TOKEN, PREFIX, BAD_REPUTATION_DURATION, SWEAR_MUTE_DURATION,
                    SWEAR_THRESHOLD, GOOD_ROLE, CHECK_BAD_WORDS)
from scripts.role_manager import RoleManager
from scripts.general import GeneralFunctions
from scripts.support import get_profanity
from datetime import datetime, timedelta
from scripts.timer import Timer


timers = {}


def run():
    bot = discord.Bot(intents=discord.Intents.all(), prefix=PREFIX)
    role_manager = RoleManager(bot)
    funcs = GeneralFunctions(bot)

    @bot.event
    async def on_connect():
        bot.load_extension("cogs.admin")
        bot.load_extension("cogs.user")
        bot.load_extension("cogs.timer")
        await bot.sync_commands()

    @bot.event
    async def on_ready():
        await role_manager.setup_roles()
        print(bot.get_all_channels())
        timers["minute"] = Timer(timedelta(minutes=1), every_minute, repeat=True)
        await timers["minute"].start()

        for role in await bot.guilds[0].fetch_roles():
            if role.name == GOOD_ROLE:
                for member in bot.guilds[0].members:
                    await member.add_roles()

    async def every_minute():
        if not ("hour" in timers.keys()) and int(datetime.now().strftime("%M")) == 0:
            print("Threshold")
            timers["hour"] = Timer(timedelta(hours=1), every_hour, repeat=True)
            await timers["hour"].start()

    async def every_hour():
        if int(datetime.now().strftime("%H")) == 7:
            print("HOUR", int(datetime.now().strftime("%S")))
            # send phrase

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user:
            return

        bad_words = get_profanity(message.content)

        if bad_words[3] and CHECK_BAD_WORDS:
            funcs.bad_counter[message.author] = funcs.bad_counter.setdefault(message.author, 0) + 1
            if funcs.bad_counter[message.author] >= SWEAR_THRESHOLD:
                await funcs.mute_member(message, SWEAR_MUTE_DURATION * (funcs.bad_counter[message.author] - 2))
                await funcs.decrease_reputation(message, BAD_REPUTATION_DURATION * (funcs.bad_counter[message.author] - 2))
            else:
                await funcs.on_swear(message)

            await message.channel.send(f"{message.author.mention} сказал: {bad_words[0].replace("[beep]", "АТАТА")}")
            await message.delete()
            return

    @bot.event
    async def on_member_join(member: discord.Member):
        await member.add_roles(discord.utils.get(bot.guilds[0].roles, name=GOOD_ROLE))

    bot.run(TOKEN)


if __name__ == '__main__':
    run()

