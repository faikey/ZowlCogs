import discord
from .utils import CustomRolesUtils
from redbot.core import Config


class CustomRolesCore:
    def __init__(self, bot):
        self.bot = bot
        self.identifier = 26556568

        self.config = Config.get_conf(self, identifier=self.identifier)
        default_guild = {
            'roles': []
        }
        self.config.register_guild(**default_guild)

        self.utils = CustomRolesUtils(self.config, self.bot)

    async def cog_list_roles(self, guild):
        message = '```'
        if await self.config.guild(guild).roles():
            for id in await self.config.guild(guild).roles():
                role = await self.utils.get_role(guild, id)
                if role:
                    message += '{} ({})\n'.format(role.name, id)
            message += '```'
            return message
        else:
            return 'No roles added to CustomRoles yet.'

    async def member_apply_role(self, member, guild, role):
        if await self.utils.cog_has_role(guild, role):
            try:
                await member.add_roles(role)
                return 'Role applied!'
            except discord.Forbidden:
                return 'I need permissions to manage roles before I can do this.'
        else:
            return 'This role is not part of CustomRoles.'

    async def member_relieve_role(self, member, guild, role):
        if await self.utils.cog_has_role(guild, role):
            try:
                await member.remove_roles(role)
                return 'Role relieved!'
            except discord.Forbidden:
                return 'I need permissions to manage roles before I can do this.'
        else:
            return 'This role is not part of CustomRoles.'

    async def guild_add_role(self, guild, role):
        if not await self.utils.cog_has_role(guild, role):
            async with self.config.guild(guild).roles() as roles:
                roles.append(role.id)
                return 'Role added to CustomRoles.'
        else:
            return 'This role is already added to CustomRoles.'

    async def guild_mass_add_role(self, context):
        guild = context.guild
        for role in guild.roles:
            if role is not guild.default_role and not await self.utils.cog_has_role(guild, role):
                question = 'Do you want to add `{}` to CustomRoles? ([Y]es/[N]o)'.format(role.name)
                answer = await self.utils.question_yes_no(question, context)
                if answer:
                    await context.send(await self.guild_add_role(guild, role))
        return 'All Done!'

    async def guild_remove_role(self, guild, role):
        if await self.utils.cog_has_role(guild, role):
            async with self.config.guild(guild).roles() as roles:
                roles.remove(role.id)
            return 'Role removed!'
        else:
            return 'This role is not part of CustomRoles.'

    async def guild_create_role(self, guild, name, color):
        if await self.utils.is_valid_color(color):
            color = await self.utils.to_discord_color(color)
            try:
                role = await guild.create_role(name=name,
                                               color=color,
                                               permissions=discord.Permissions(permissions=0),
                                               hoist=False,
                                               reason='Created for CustomRoles')
                async with self.config.guild(guild).roles() as roles:
                    roles.append(role.id)
                return 'Role created!'
            except discord.Forbidden:
                return 'I need permissions to manage roles before I can do this.'
        else:
            return '{} is not a valid hexidecimal color.'.format(color)

    async def guild_delete_role(self, guild, role):
        if await self.utils.cog_has_role(guild, role):
            try:
                await role.delete()
                async with self.config.guild(guild).roles() as roles:
                    roles.remove(role.id)
                return 'Role deleted!'
            except discord.Forbidden:
                return 'I need permissions to manage roles before I can do this.'
        else:
            return 'This role is not part of CustomRoles.'
