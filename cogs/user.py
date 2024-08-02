from discord.ext import commands
import discord


class UserCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.slash_command(description="Удаляет твои сообщения в этом канале")
    async def clear_me(self, ctx: discord.commands.context.ApplicationContext, limit=100):
        length = len(await ctx.channel.purge(limit=int(limit), check=lambda m: m.author == ctx.author))
        await ctx.respond(f"Я очистил **{length}** сообщений *{ctx.author}*")


def setup(bot):
    bot.add_cog(UserCog(bot))
