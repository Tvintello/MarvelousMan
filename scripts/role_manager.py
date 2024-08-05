from discord.ext import commands
import discord
from config import ROLES, BAD_ROLE, GOOD_ROLE


class RoleManager:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.available_roles = [role[0] for role in ROLES]

    def get_current_role(self, member: discord.Member):
        for role in member.roles:
            if role.name in self.available_roles:
                return role
        return discord.utils.get(self.bot.guilds[0].roles, name="@everyone")

    async def get_cosmetic_role(self, member: discord.Member):
        for role in member.roles:
            if not (role.name in self.available_roles) and role.name != "@everyone":
                return role

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
        for role in ROLES:
            await self.setup_role(*role)

    async def set_role(self, member: discord.Member, role_name: str):
        new_role = discord.utils.get(self.bot.guilds[0].roles, name=role_name)
        length = len(self.bot.guilds[0].roles)
        for role in await self.bot.guilds[0].fetch_roles():
            if role.name in self.available_roles:
                await member.remove_roles(role)
            elif (not (role.name in self.available_roles) and role.name != "@everyone"
                  and role.name != self.bot.user.name):
                await role.edit(position=length-2)

        if role_name == BAD_ROLE:
            await new_role.edit(position=length - 2)
        await member.add_roles(new_role)

    async def set_cosmetic_role(self, member: discord.Member, role_name: str, color: str):
        if role_name in self.available_roles:
            return

        for role in member.roles:
            if (not (role.name in self.available_roles) and role.name != "@everyone"
                    and role.name != self.bot.user.name):
                await member.remove_roles(role)  # Удаляет все косметические роли с участника
                await role.delete()  # Удаляет эти роли с сервера

        await self.setup_role(role_name, discord.Permissions.none(), color)
        new_role = discord.utils.get(self.bot.guilds[0].roles, name=role_name)
        await member.add_roles(new_role)
        length = len(self.bot.guilds[0].roles)
        bad = discord.utils.get(self.bot.guilds[0].roles, name=BAD_ROLE)
        await bad.edit(position=length-2)
        good = discord.utils.get(self.bot.guilds[0].roles, name=GOOD_ROLE)
        await good.edit(position=1)
        await new_role.edit(position=length-3)







