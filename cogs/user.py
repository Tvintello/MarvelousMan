from discord.ext import commands
import discord
from scripts.support import get_json, get_profanity
from random import choice, randint
from scripts.role_manager import RoleManager
from config import BAD_ROLE, BAD_REPUTATION_DURATION, SAY_THRESHOLD, SAY_DURATION
from scripts.general import GeneralFunctions
from datetime import timedelta


say_counter = {}
phrases = get_json("./phrases.json")


class UserCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.role_manager = RoleManager(self.bot)
        self.funcs = GeneralFunctions(self.bot)

    @discord.slash_command(description="Выводит случайное число в данном диапазоне")
    async def randomize(self, ctx: discord.commands.context.ApplicationContext, minimum: int, maximum: int):
        number = randint(minimum, maximum)
        await ctx.respond(f"Выпало число: {number}")

    @discord.slash_command(description="Выводит случайное слово из предложенных")
    async def randomize_words(self, ctx: discord.commands.context.ApplicationContext, words: str):
        delimiters = (" ", ",", "|", "\\", "/", ".", ";")
        new_words = []
        word = ""
        for let in words:
            if let in delimiters:
                if word:
                    new_words.append(word)
                    word = ""
            else:
                word += let
        new_words.append(word)
        print(new_words)
        await ctx.respond(f"Выпало слово: {choice(new_words)}")

    @discord.slash_command(description="Устанавливает косметическую роль, которая не выполняет никаких функций. "
                                       "Нужна для смены цвета ника")
    async def set_cosmetic_role(self, ctx: discord.commands.context.ApplicationContext, color: str, name: str):
        await ctx.response.defer()
        try:
            color = getattr(discord.Colour, color)
        except KeyError:
            await ctx.respond("Я не знаю такого цвета, извини")
            return

        await self.role_manager.set_cosmetic_role(ctx.user, name, color())
        await ctx.followup.send(f"По просьбе {ctx.user.mention} я поставил новую косметическую роль")

    @discord.slash_command(description="Цензурит переданное сообщение")
    async def censor(self, ctx: discord.commands.context.ApplicationContext, message: str):
        await ctx.response.defer()
        bad_words = get_profanity(message)
        new_words = []
        for word in bad_words[3]:
            word = word[:len(word) // 2] + "#" * (len(word) - len(word) // 2)
            new_words.append(word)

        words = bad_words[0].split()
        count = 0
        content = []
        for word in words:
            if word == "[beep]":
                content.append(new_words[count])
                count += 1
            else:
                content.append(word)

        await ctx.followup.send(f"**{ctx.user.display_name}**: {" ".join(content)}")

    @discord.slash_command(description="Удаляет твои сообщения в этом канале")
    async def clear_me(self, ctx: discord.commands.context.ApplicationContext, limit=100):
        await ctx.response.defer()
        length = len(await ctx.channel.purge(limit=int(limit), check=lambda m: m.author == ctx.author))
        await ctx.followup.send(f"Я очистил **{length}** сообщений *{ctx.author}*")

    @discord.slash_command(description="Заставляет бота сказать то, что ты ему скажешь")
    async def say(self, ctx: discord.commands.context.ApplicationContext, message):
        def reset_say_counter():
            say_counter[ctx.user] = 0
            print("RESET SAY")

        say_counter[ctx.user] = say_counter.setdefault(ctx.user, 0) + 1
        await self.funcs.reset_timer(SAY_DURATION, reset_say_counter, ctx.user, "say")
        if say_counter[ctx.user] >= SAY_THRESHOLD:
            await ctx.user.timeout_for(timedelta(minutes=5))
            await self.funcs.decrease_reputation(BAD_REPUTATION_DURATION, ctx.user)
            await ctx.respond(choice(phrases["on_say"]))
        elif self.role_manager.get_current_role(ctx.user).name == BAD_ROLE:
            await ctx.respond(choice(phrases["on_bad_say"]))
        else:
            await ctx.respond(message)

    @discord.slash_command(description="Позволяет получить аватар участника")
    async def get_avatar(self, ctx: discord.commands.context.ApplicationContext, user_name: str = ""):
        if user_name:
            for user in self.bot.get_all_members():
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


def setup(bot):
    bot.add_cog(UserCog(bot))
