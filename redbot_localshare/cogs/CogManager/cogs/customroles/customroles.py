from discord.ext import commands
import discord

from .core import CustomRolesCore
from .events import CustomRolesEventsMixIn


class CustomRoles(CustomRolesEventsMixIn):
    def __init__(self, bot):
        self.bot = bot
        self.core = CustomRolesCore(self.bot)

    @commands.group(name='customroles', aliases=['cr'])
    async def customroles(self, context):
        if context.invoked_subcommand is None:
            await context.send_help()

    @customroles.group(name='list')
    async def customroles_list(self, context):
        '''Shows a list with all possible roles that can be engaged.'''
        message = await self.core.cog_list_roles(context.guild)
        await context.send(message)

    @customroles.group(name='engage', aliases=['apply'])
    async def customroles_apply(self, context, *, role: discord.Role):
        '''Engage a role from to a member'''
        message = await self.core.member_apply_role(context.author, context.guild, role)
        await context.send(message)

    @customroles.group(name='disengage', aliases=['relieve'])
    async def customroles_relieve(self, context, *, role: discord.Role):
        '''Disengage a role from a member'''
        message = await self.core.member_relieve_role(context.author, context.guild, role)
        await context.send(message)

    @customroles.group(name='massadd')
    @commands.has_permissions(administrator=True)
    async def customroles_massadd(self, context):
        '''Add existing roles to CustomRoles (for servers with a large number of roles to be added)'''
        message = await self.core.guild_mass_add_role(context)
        await context.send(message)

    @customroles.group(name='add')
    @commands.has_permissions(administrator=True)
    async def customroles_add(self, context, *, role: discord.Role):
        '''Add an existing role to CustomRoles'''
        message = await self.core.guild_add_role(context.guild, role)
        await context.send(message)

    @customroles.group(name='create')
    @commands.has_permissions(administrator=True)
    async def customroles_create(self, context, color: str, *, name: str):
        '''Create a new role for CustomRoles'''
        message = await self.core.guild_create_role(context.guild, name, color)
        await context.send(message)

    @customroles.group(name='remove')
    @commands.has_permissions(administrator=True)
    async def customroles_remove(self, context, *, role: discord.Role):
        '''Removes a role from CustomRoles'''
        message = await self.core.guild_remove_role(context.guild, role)
        await context.send(message)

    @customroles.group(name='delete')
    @commands.has_permissions(administrator=True)
    async def customroles_delete(self, context, *, role: discord.Role):
        '''Deletes a role entirely from the server'''
        message = await self.core.guild_delete_role(context.guild, role)
        await context.send(message)
