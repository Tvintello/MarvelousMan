from discord.ext import commands
import discord
from config import roles


class RoleManager:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.available_roles = [role[0] for role in roles]

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

    async def setup_roles(self):
        for role in roles:
            await self.setup_role(*role)

    async def set_role(self, member: discord.Member, role_name: str):
        new_role = discord.utils.get(self.bot.guilds[0].roles, name=role_name)

        for role in await self.bot.guilds[0].fetch_roles():
            if role.name in self.available_roles:
                await member.remove_roles(role)
            elif (not (role.name in self.available_roles) and role.name != "@everyone"
                  and role.name != self.bot.user.name):
                length = len(await self.bot.guilds[0].fetch_roles())
                await role.edit(position=length-2)
        await member.add_roles(new_role)




