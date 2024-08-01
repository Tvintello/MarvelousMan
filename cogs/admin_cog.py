from discord.ext import commands
import discord


class AdminCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.slash_command()
    async def clear(self, ctx: discord.commands.context.ApplicationContext, whose: str = "all", limit=100):
        if whose == "all":
            length = len(await ctx.channel.purge(limit=limit))
            await ctx.respond(f"Я очистил **{length}** улик ваших деяний")

    @discord.slash_command(description="Мутит участника")
    async def mute(self, ctx: discord.commands.context.ApplicationContext):
        await ctx.respond()

    @discord.slash_command(description="Убирает мут с участника")
    async def unmute(self, ctx: discord.commands.context.ApplicationContext):
        await ctx.respond()


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(AdminCog(bot))
