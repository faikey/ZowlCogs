import discord
import re


class CustomRolesUtils:
    def __init__(self, config, bot):
        self.config = config
        self.bot = bot

    async def get_role(self, guild, id):
        role = [role for role in guild.roles if role.id == id and role.id in await self.config.guild(guild).roles()]
        return role[0] if role else False

    async def is_valid_color(self, color):
        return True if re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', color) else False

    async def to_discord_color(self, color):
        return discord.Color(int(color, 16))

    async def cog_has_role(self, guild, role):
        if role.id in await self.config.guild(guild).roles():
            return True
        return False

    async def question_yes_no(self, question, context):
        def check(message):
            return context.author.id == message.author.id
        await context.send(question)

        try:
            message = await self.bot.wait_for('message', timeout=120, check=check)
        except TimeoutError:
            pass
        if message:
            if any(n in message.content.lower() for n in ['yes', 'y']):
                return True
        return False
