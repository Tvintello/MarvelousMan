from discord.ext import commands
import discord


class BotCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(BotCog(bot))
