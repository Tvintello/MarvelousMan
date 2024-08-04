import discord

from config import TOKEN, PREFIX, COLOR_GREEN
from censure import Censor  # https://github.com/Priler/samurai/tree/main/censure
from scripts.support import get_json
from scripts.role_manager import RoleManager
from scripts.general import GeneralFunctions

censor_ru = Censor.get(lang="ru")
phrases = get_json("phrases.json")


def get_profanity(text):
    info = censor_ru.clean_line(text)
    return info[3]


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = discord.Bot(intents=intents, prefix=PREFIX)
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
                await funcs.decrease_reputation(message)
                await funcs.mute_member(message)
            return
        elif not message.content.startswith("/"):
            await message.channel.send(message.content)

    bot.run(TOKEN)


if __name__ == '__main__':
    run()

