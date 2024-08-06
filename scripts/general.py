from discord.ext import commands
import discord
from scripts.timer import Timer
from random import choice
from scripts.support import get_json
from scripts.role_manager import RoleManager
from config import BAD_ROLE, GOOD_ROLE


phrases = get_json("./phrases.json")


class GeneralFunctions:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.timers = {}
        self.bad_counter = {}
        self.bot = bot
        self.role_manager = RoleManager(self.bot)

    async def on_swear(self, message):
        await message.reply(choice(phrases["on_swear"]))

    async def on_mute_ended(self, message, phrase):
        await message.reply(phrase)

    async def mute_member(self, message, duration):
        async def launch_on_mute_ended():
            await self.on_mute_ended(message, choice(phrases["on_mute_end"]))

        try:
            await message.author.timeout_for(duration)
        except discord.Forbidden:
            pass
        await message.reply(choice(phrases["on_mute"]))
        if self.timers.get(message.author) and not self.timers[message.author].get("mute"):
            self.timers[message.author]["mute"] = Timer(duration, launch_on_mute_ended)
            await self.timers[message.author]["mute"].start()
        elif not self.timers.get(message.author):
            self.timers[message.author] = {}

    async def retrieve_reputation(self, message: discord.Message):
        self.bad_counter[message.author] = 0
        await self.role_manager.set_role(message.author, GOOD_ROLE)
        await message.channel.send(f"{message.author.mention} {choice(phrases["on_retrieve_reputation"])}")

    async def decrease_reputation(self, message: discord.Message, duration):
        async def launch_retrieve_reputation():
            await self.retrieve_reputation(message)

        await self.reset_timer(duration, launch_retrieve_reputation, message.author, "reputation")
        await self.role_manager.set_role(message.author, BAD_ROLE)

    async def reset_timer(self, duration, func, user, timer_name):
        if self.timers.get(user) and self.timers[user].get(timer_name):
            await self.timers[user][timer_name].stop()
        else:
            self.timers[user] = {}

        self.timers[user][timer_name] = Timer(duration, func)
        await self.timers[user][timer_name].start()


def setup(bot):
    bot.add_cog(GeneralFunctions(bot))
