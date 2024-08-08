from discord.ext import commands
import discord
from config import MAIN_CHANNEL_ID


class AdminCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.slash_command(description="Удаляет историю канала, можно настроить чьи сообщения удалить")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: discord.Interaction, whose: str = "all", limit=100):
        await ctx.response.defer()
        main_channel = self.bot.get_channel(MAIN_CHANNEL_ID)
        id_ = await ctx.original_message()
        if whose == "all":
            length = len(await ctx.channel.purge(limit=int(limit), check=lambda m: self.is_message(m, id_)))
            await main_channel.send(f"Я очистил **{length}** улик ваших деяний")
        elif whose == "bot":
            length = len(await ctx.channel.purge(limit=int(limit), check=lambda m: self.is_bot(m, id_)))
            await main_channel.send(f"Я очистил **{length}** своих сообщений")
        else:
            for mem in self.bot.get_all_members():
                if mem.name.lower() == whose.lower():
                    whose = mem
                    break
            else:
                await main_channel.send(f"На этом сервере нет *{whose}*")
                return
            length = len(await ctx.channel.purge(limit=int(limit), check=lambda m: self.is_member(m, whose, id_)))
            await main_channel.send(f"Я очистил **{length}** сообщений *{whose}*")



        await ctx.followup.send()

    def is_bot(self, message, command_id) -> bool:
        return message.author == self.bot.user and command_id != message.id

    def is_member(self, message: discord.Message, member, command_id) -> bool:
        return message.author == member and command_id != message.id

    def is_message(self, message: discord.Message, command_id):
        return message.id != command_id

    @discord.slash_command(description="Убирает мут с участника")
    @commands.has_permissions(administrator=True)
    async def remove_timeout(self, ctx: discord.commands.context.ApplicationContext, member: discord.Member, reason=""):
        await member.remove_timeout(reason=reason)
        await ctx.respond(f"С {member} снят мут в текстовых каналах")


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(AdminCog(bot))
