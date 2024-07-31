import discord
from discord import Message
from discord.ext import commands
from config import TOKEN, PREFIX, COLOR_RED
from censure import Censor
from scripts.support import get_json
from random import choice

ins = discord.Intents.default()
ins.message_content = True
bot = commands.Bot(PREFIX, intents=ins)

censor_ru = Censor.get(lang="ru")
phrases = get_json("scripts/phrases.json")


bad_counter = {}


class BotCog(commands.Cog):
    role_name = "role name"

    def __init__(self, bot):
        self.bot = bot

    async def setup_role(self):
        exists = False
        for role in await self.bot.guilds[0].fetch_roles():
            if role.name == self.role_name:
                exists = True
                break
        if exists:
            return

        await self.bot.guilds[0].create_role(
            name=self.role_name,
            color=COLOR_RED,
            hoist=True,
            permissions=
        )


def get_profanity(text):
    info = censor_ru.clean_line(text)
    return info[3]


@bot.event
async def on_message(message: Message) -> None:
    ctx = await bot.get_context(message)
    if message.author != bot.user:
        await bot.process_commands(message)

        if get_profanity(message.content):
            bad_counter[message.author] = bad_counter.setdefault(message.author, 0) + 1
            role = discord.utils.get(message.author.roles, name="MUTED")
            bot.get_context()
            await message.author.add_roles(role)
            print(bad_counter)
            await ctx.send(choice(phrases["on_swear"]))
            return

        if not message.content.startswith(PREFIX):
            await ctx.send(message.content)


@bot.command()
async def say(ctx, message):
    await ctx.send(message)


async def setup_bot(bot):
    cog = BotCog(bot)
    await bot.add_cog(cog)
    await cog.setup_role()


if __name__ == '__main__':
    bot.run(TOKEN)

