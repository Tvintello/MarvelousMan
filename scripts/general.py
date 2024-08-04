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
        self.bad_counter[message.author] = self.bad_counter.setdefault(message.author, 0) + 1
        await message.channel.send(choice(phrases["on_swear"]))

    async def on_mute_ended(self, message, phrase):
        await message.channel.send(f"{message.author.mention} {phrase}")

    async def mute_member(self, message, duration):
        async def launch_on_mute_ended():
            await self.on_mute_ended(message, choice(phrases["on_mute_end"]))

        # await message.author.timeout_for(mute_duration)
        await message.channel.send(choice(phrases["on_mute"]))
        if self.timers[message.author] and not self.timers[message.author].get("mute"):
            self.timers[message.author]["mute"] = Timer(duration, launch_on_mute_ended)
            await self.timers[message.author]["mute"].start()
        elif not self.timers[message.author]:
            self.timers[message.author] = {}

    async def retrieve_reputation(self, member: discord.Member):
        self.bad_counter[member] = 0
        await self.role_manager.set_role(member, GOOD_ROLE)
        print(f"RESET BAD COUNTER: {self.bad_counter}")

    async def decrease_reputation(self, duration, user):
        async def launch_retrieve_reputation():
            await self.retrieve_reputation(user)

        if self.timers.get(user) and self.timers[user].get("reputation"):
            await self.timers[user]["reputation"].stop()
        else:
            self.timers[user] = {}

        await self.role_manager.set_role(user, BAD_ROLE)
        self.timers[user]["reputation"] = Timer(duration, launch_retrieve_reputation)
        await self.timers[user]["reputation"].start()


def setup(bot):
    bot.add_cog(GeneralFunctions(bot))
