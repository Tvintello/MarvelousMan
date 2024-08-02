from discord.ext import commands
import discord


class RoleManager:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    async def setup_role(self, role_name, permissions, color):
        exists = False
        for role in await self.bot.guilds[0].fetch_roles():
            if role.name == role_name:
                exists = True
                break
        if exists:
            return

        await self.bot.guilds[0].create_role(
            name=role_name,
            color=color,
            hoist=True,
            permissions=permissions
        )

