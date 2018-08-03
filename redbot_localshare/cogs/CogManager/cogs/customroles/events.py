from .core import CustomRolesCore


class CustomRolesEventsMixIn:
    def __init__(self):
        self.core = CustomRolesCore()

    async def on_guild_role_delete(self, role):
        guild = role.guild
        roles = await self.core.config.guild(guild).roles()
        if role.id in roles:
            await self.core.guild_remove_role(guild, role)
