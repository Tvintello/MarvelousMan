from discord.ext import commands
import discord
from scripts.support import get_json
from random import choice
from scripts.role_manager import RoleManager
from config import BAD_ROLE, BAD_REPUTATION_DURATION, SAY_THRESHOLD
from scripts.general import GeneralFunctions
from datetime import timedelta


say_counter = {}
phrases = get_json("./phrases.json")


class UserCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.role_manager = RoleManager(self.bot)
        self.funcs = GeneralFunctions(self.bot)

    @discord.slash_command(description="Удаляет твои сообщения в этом канале")
    async def clear_me(self, ctx: discord.commands.context.ApplicationContext, limit=100):
        length = len(await ctx.channel.purge(limit=int(limit), check=lambda m: m.author == ctx.author))
        await ctx.respond(f"Я очистил **{length}** сообщений *{ctx.author}*")

    @discord.slash_command(description="Заставляет бота сказать то, что ты ему скажешь")
    async def say(self, ctx: discord.commands.context.ApplicationContext, message):
        say_counter[ctx.user] = say_counter.setdefault(ctx.user, 0) + 1
        if say_counter[ctx.user] >= SAY_THRESHOLD:
            # await ctx.user.timeout_for(timedelta(minutes=5))
            await self.funcs.decrease_reputation(BAD_REPUTATION_DURATION, ctx.user)
            await ctx.respond(choice(phrases["on_say"]))
            say_counter[ctx.user] = 0
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
