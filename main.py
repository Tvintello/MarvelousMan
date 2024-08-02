import discord

from config import TOKEN, PREFIX, COLOR_RED, COLOR_GREEN, DECENT
from censure import Censor  # https://github.com/Priler/samurai/tree/main/censure
from scripts.support import get_json
from random import choice
from datetime import timedelta
from scripts.timer import Timer

censor_ru = Censor.get(lang="ru")
phrases = get_json("scripts/phrases.json")

bad_counter = {}
user_backend_timers = {}
say_counter = {}


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

    @bot.event
    async def on_connect():
        bot.load_extension("cogs.admin")
        bot.load_extension("cogs.user")
        bot.load_extension("cogs.timer")
        await bot.sync_commands()

    @bot.event
    async def on_ready():
        global mute_role

        await setup_role("Приличный", DECENT, COLOR_GREEN)

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
        print(bad_counter)

        if get_profanity(message.content):
            bad_counter[message.author] = bad_counter.setdefault(message.author, 0) + 1
            await message.channel.send(choice(phrases["on_swear"]))
            if bad_counter[message.author] >= 3:
                await message.author.timeout_for(timedelta(minutes=5 * (bad_counter[message.author] - 2)))
                # if bad_counter[message.author] >= 12:
                #     await message.channel.send("/tenor query: гигачад")
                await message.channel.send(choice(phrases["on_mute"]))
                user_backend_timers[message.author] = Timer(timedelta(hours=(bad_counter[message.author] - 2)),
                                                                      lambda: reset_bad_counter(message.author))
                await user_backend_timers[message.author].start()
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
                if ctx.user.name.lower() == user_name.lower():
                    await ctx.respond(ctx.user.avatar)
                else:
                    await ctx.respond("Нет такого участника, ты че то попутал")
        else:
            await ctx.respond(ctx.user.avatar)

    bot.run(TOKEN)


if __name__ == '__main__':
    run()

