import discord

from config import TOKEN, PREFIX, BAD_REPUTATION_DURATION, SWEAR_MUTE_DURATION, SWEAR_THRESHOLD, GOOD_ROLE
from censure import Censor  # https://github.com/Priler/samurai/tree/main/censure
from scripts.role_manager import RoleManager
from scripts.general import GeneralFunctions

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
            if role.name == GOOD_ROLE:
                for member in bot.guilds[0].members:
                    await member.add_roles()

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user:
            return

        if get_profanity(message.content):
            await funcs.on_swear(message)
            if funcs.bad_counter[message.author] >= SWEAR_THRESHOLD:
                await funcs.decrease_reputation(BAD_REPUTATION_DURATION * (funcs.bad_counter[message.author] - 2),
                                                message.author)
                await funcs.mute_member(message, SWEAR_MUTE_DURATION * (funcs.bad_counter[message.author] - 2))
            return

    @bot.event
    async def on_member_join(member: discord.Member):
        await member.add_roles(discord.utils.get(bot.guilds[0].roles, name=GOOD_ROLE))

    bot.run(TOKEN)


if __name__ == '__main__':
    run()

