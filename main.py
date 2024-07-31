import discord
from discord import Message
from discord.ext import commands
from config import TOKEN, PREFIX
from censure import Censor
from scripts.support import get_json
from random import choice

ins = discord.Intents.default()
ins.message_content = True
bot = commands.Bot(PREFIX, intents=ins)

censor_ru = Censor.get(lang="ru")
phrases = get_json("scripts/phrases.json")


def get_profanity(text):
    info = censor_ru.clean_line(text)
    return info[3]


@bot.event
async def on_message(message: Message) -> None:
    ctx = await bot.get_context(message)
    if message.author != bot.user:
        await bot.process_commands(message)

        if get_profanity(message.content):
            await ctx.send(choice(phrases["on_swear"]))
            return

        if not message.content.startswith(PREFIX):
            await ctx.send(message.content)


@bot.command()
async def say(ctx, message):
    await ctx.send(message)


if __name__ == '__main__':
    bot.run(TOKEN)

