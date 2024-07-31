from discord.ext import commands
import discord
from config import COLOR_RED


class BotCog(commands.Cog):
    role_name = "Замученный"

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    async def setup_role(self):
        exists = False
        for role in await self.bot.guilds[0].fetch_roles():
            if role.name == self.role_name:
                exists = True
                break
        if exists:
            return

        permissions = discord.Permissions.none()
        permissions.view_channel = True
        await self.bot.guilds[0].create_role(
            name=self.role_name,
            color=COLOR_RED,
            hoist=True,
            permissions=permissions
        )


async def setup(bot):
    cog = BotCog(bot)
    await bot.add_cog(cog)
    await cog.setup_role()