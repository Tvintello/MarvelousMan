from discord.ext import commands
import discord


class AdminCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.slash_command(description="Удаляет историю канала, можно настроить чьи сообщения удалить")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: discord.commands.context.ApplicationContext, whose: str = "all", limit=100):
        if whose == "all":
            length = len(await ctx.channel.purge(limit=int(limit)))
            await ctx.respond(f"Я очистил **{length}** улик ваших деяний")
        elif whose == "bot":
            length = len(await ctx.channel.purge(limit=int(limit), check=self.is_bot))
            await ctx.respond(f"Я очистил **{length}** своих сообщений")
        else:
            for mem in self.bot.get_all_members():
                if mem.name.lower() == whose.lower():
                    whose = mem
            print(whose)
            length = len(await ctx.channel.purge(limit=int(limit), check=lambda m: self.is_member(m, whose)))
            await ctx.respond(f"Я очистил **{length}** сообщений *{whose}*")

    def is_bot(self, message) -> bool:
        return message.author == self.bot.user

    def is_member(self, message, member) -> bool:
        return message.author == member

    @discord.slash_command(description="Убирает мут с участника")
    @commands.has_permissions(administrator=True)
    async def remove_timeout(self, ctx: discord.commands.context.ApplicationContext, member: discord.Member, reason=""):
        await member.remove_timeout(reason=reason)
        await ctx.respond(f"С {member} снят мут в текстовых каналах")


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(AdminCog(bot))
