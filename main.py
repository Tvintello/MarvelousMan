import discord

from config import TOKEN, PREFIX, COLOR_GREEN
from censure import Censor  # https://github.com/Priler/samurai/tree/main/censure
from scripts.role_manager import RoleManager
from scripts.general import GeneralFunctions
from datetime import timedelta

censor_ru = Censor.get(lang="ru")


def get_profanity(text):
    info = censor_ru.clean_line(text)
    return info[3]


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

        for role in await bot.guilds[0].fetch_roles():
            if role.name == "Приличный":
                for member in bot.guilds[0].members:
                    await member.add_roles()

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user:
            return

        if get_profanity(message.content):
            await funcs.on_swear(message)
            if funcs.bad_counter[message.author] >= 3:
                await funcs.decrease_reputation(message, timedelta(hours=2 * (funcs.bad_counter[message.author] - 2)))
                await funcs.mute_member(message, timedelta(minutes=30 * (funcs.bad_counter[message.author] - 2)))
            return
        elif not message.content.startswith("/"):
            await message.channel.send(message.content)

    @bot.event
    async def on_member_join(member: discord.Member):
        await member.add_roles(discord.utils.get(bot.guilds[0].roles, name="Приличный"))

    bot.run(TOKEN)


if __name__ == '__main__':
    run()

