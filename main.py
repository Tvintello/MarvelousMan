import discord
from discord import Message
from discord.ext import commands
from config import TOKEN, PREFIX
from censure import Censor
from scripts.support import get_json
from random import choice

# TODO: пай скрипт для BotCog и runner приложения https://www.youtube.com/watch?v=2iA66BnKWis

censor_ru = Censor.get(lang="ru")
phrases = get_json("scripts/phrases.json")
mute_role = discord.abc.Snowflake

bad_counter = {}


def get_profanity(text):
    info = censor_ru.clean_line(text)
    return info[3]


def run():
    ins = discord.Intents.default()
    ins.message_content = True
    bot = commands.Bot(PREFIX, intents=ins)

    @bot.event
    async def on_ready():
        global mute_role
        await bot.load_extension("scripts.bot_cog")
        for role in await bot.guilds[0].fetch_roles():
            if role.name == "Замученный":
                mute_role = role
                break

    @bot.event
    async def on_message(message: Message) -> None:
        ctx = await bot.get_context(message)
        if message.author != bot.user:
            await bot.process_commands(message)

            if get_profanity(message.content):
                bad_counter[message.author] = bad_counter.setdefault(message.author, 0) + 1
                await message.author.add_roles(mute_role)
                await ctx.send(choice(phrases["on_swear"]))
                return

            if not message.content.startswith(PREFIX):
                await ctx.send(message.content)

    @bot.command()
    async def say(ctx, *message):
        await ctx.send(" ".join(message))

    # @tree.command(name="get avatar", description="description")
    # async def get_avatar(inter: discord.Interaction, user_name: str = ""):
    #     if user_name:
    #         for user in bot.get_all_members():
    #             print(user.name)
    #             if user.name == user_name:
    #                 print(user.avatar)
    #                 break
    #         else:
    #             print(inter.context.author.name)
    #             if inter.context.author.name == user_name.lower():
    #                 await inter.response.send_message(inter.context.author.avatar)
    #     else:
    #         await inter.response.send_message(inter.context.author.avatar)

    bot.run(TOKEN)


if __name__ == '__main__':
    run()

