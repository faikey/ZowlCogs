import asyncio
from typing import List, Union

import discord
from discord.ext import commands

from redbot.core import Config, checks
from redbot.core.bot import Red


class ReactRoleCombo:
    def __init__(self, message_id, role_id, emoji=None, is_custom_emoji=False):
        self.message_id = message_id
        self.role_id = role_id
        self.emoji = emoji

        self.is_custom_emoji = is_custom_emoji

    def __eq__(self, other: "ReactRoleCombo"):
        return (
            self.message_id == other.message_id and
            self.role_id == other.role_id and
            self.emoji == other.emoji
        )

    def to_json(self):
        return {
            'message_id': self.message_id,
            'role_id': self.role_id,
            'emoji': self.emoji,
            'is_custom_emoji': self.is_custom_emoji
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            data['message_id'],
            data['role_id'],
            data['emoji'],
            data['is_custom_emoji']
        )


class ReactRole:
    """
    This cog enables role assignment/removal based on reactions to specific
    messages.
    """

    def __init__(self, red: Red):
        self.bot = red
        self.config = Config.get_conf(self, 3203948230954902384,
                                      force_registration=True)
        self.config.register_global(
            registered_combos=[]
        )

    async def combo_list(self) -> List[ReactRoleCombo]:
        """
        Returns a list of reactrole combos.

        :return:
        """
        cmd = self.config.registered_combos()

        return [ReactRoleCombo.from_json(data) for data in await cmd]

    async def set_combo_list(self, combo_list: List[ReactRoleCombo]):
        """
        Helper method to set the list of reactrole combos.

        :param combo_list:
        :return:
        """
        raw = [combo.to_json() for combo in combo_list]
        await self.config.registered_combos.set(raw)

    async def is_registered(self, message_id: int) -> bool:
        """
        Determines if a message ID has been registered.

        :param message_id:
        :return:
        """
        return any(message_id == combo.message_id
                   for combo in await self.combo_list())

    async def add_reactrole(self, message_id: int, emoji: Union[str, int], role: discord.Role):
        """
        Adds a react|role combo.

        :param int message_id:
        :param str or int emoji:
        :param discord.Role role:
        """
        is_custom = True
        if isinstance(emoji, str):
            is_custom = False

        combo = ReactRoleCombo(message_id, role.id, emoji=emoji, is_custom_emoji=is_custom)

        current_combos = await self.combo_list()

        if combo not in current_combos:
            current_combos.append(combo)
            await self.set_combo_list(current_combos)

    async def remove_react(self, message_id: int, emoji: Union[int, str]):
        """
        Removes a given reaction.

        :param int message_id:
        :param str or int emoji:
        :return:
        """
        current_combos = await self.combo_list()

        to_keep = [c for c in current_combos
                   if not (c.message_id == message_id and c.emoji == emoji)]

        if to_keep != current_combos:
            await self.set_combo_list(to_keep)

    async def has_reactrole_combo(self, message_id: int, emoji: Union[str, int])\
            -> (bool, List[ReactRoleCombo]):
        """
        Determines if there is an existing react|role combo for a given message
        and emoji ID.

        :param int message_id:
        :param str or int emoji:
        :return:
        """
        if not await self.is_registered(message_id):
            return False, []

        combos = await self.combo_list()

        ret = [c for c in combos
               if c.message_id == message_id and c.emoji == emoji]

        return len(ret) > 0, ret

    def _get_member(self, channel_id: int, user_id: int) -> discord.Member:
        """
        Tries to get a member with the given user ID from the guild that has
        the given channel ID.

        :param int channel_id:
        :param int user_id:
        :rtype:
            discord.Member
        :raises LookupError:
            If no such channel or member can be found.
        """
        channel = self.bot.get_channel(channel_id)
        try:
            member = channel.guild.get_member(user_id)
        except AttributeError as e:
            raise LookupError("No channel found.") from e

        if member is None:
            raise LookupError("No member found.")

        return member

    def _get_role(self, guild: discord.Guild, role_id: int) -> discord.Role:
        """
        Gets a role object from the given guild with the given ID.

        :param discord.Guild guild:
        :param int role_id:
        :rtype:
            discord.Role
        :raises LookupError:
            If no such role exists.
        """
        role = discord.utils.get(guild.roles, id=role_id)

        if role is None:
            raise LookupError("No role found.")

        return role

    async def _get_message(self, ctx: commands.Context, message_id: int)\
            -> Union[discord.Message, None]:
        """
        Tries to find a message by ID in the current guild context.

        :param ctx:
        :param message_id:
        :return:
        """
        for channel in ctx.guild.channels:
            try:
                return await channel.get_message(message_id)
            except discord.NotFound:
                pass
            except AttributeError: # VoiceChannel object has no attribute 'get_message'
                pass

        return None

    async def _wait_for_emoji(self, ctx: commands.Context):
        """
        Asks the user to react to this message and returns the emoji string if unicode
        or ID if custom.

        :param ctx:
        :raises asyncio.TimeoutError:
            If the user does not respond in time.
        :return:
        """
        message = await ctx.send("Please react to this message with the reaction you"
                                 " would like to add/remove, you have 20 seconds to"
                                 " respond.")

        def _wait_check(react, user):
            msg = react.message
            return msg.id == message.id and user.id == ctx.author.id

        reaction, _ = await ctx.bot.wait_for('reaction_add', check=_wait_check, timeout=20)

        try:
            ret = reaction.emoji.id
        except AttributeError:
            # The emoji is unicode
            ret = reaction.emoji

        return ret, reaction.emoji

    @commands.group()
    @checks.guildowner_or_permissions(manage_roles=True)
    async def reactrole(self, ctx: commands.Context):
        """
        Base command for this cog. Check help for the commands list.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @reactrole.command()
    async def add(self, ctx: commands.Context, message_id: int, *, role: discord.Role):
        """
        Adds a reaction|role combination to a registered message, don't use
        quotes for the role name.
        """
        message = await self._get_message(ctx, message_id)
        if message is None:
            await ctx.send("That message doesn't seem to exist.")
            return

        try:
            emoji, actual_emoji = await self._wait_for_emoji(ctx)
        except asyncio.TimeoutError:
            await ctx.send("You didn't respond in time, please redo this command.")
            return

        try:
            await message.add_reaction(actual_emoji)
        except discord.HTTPException:
            await ctx.send("I can't add that emoji because I'm not in the guild that"
                           " owns it.")
            return

        # noinspection PyTypeChecker
        await self.add_reactrole(message_id, emoji, role)

        await ctx.send("React|Role combo added.")

    @reactrole.command()
    async def remove(self, ctx: commands.Context, message_id: int):
        """
        Removes all roles associated with a given reaction.
        """
        try:
            emoji, actual_emoji = await self._wait_for_emoji(ctx)
        except asyncio.TimeoutError:
            await ctx.send("You didn't respond in time, please redo this command.")
            return

        # noinspection PyTypeChecker
        await self.remove_react(message_id, emoji)

        await ctx.send("Reaction removed.")

    async def on_raw_reaction_add(self, emoji: discord.PartialReactionEmoji,
                                  message_id: int, channel_id: int, user_id: int):
        """
        Event handler for long term reaction watching.

        :param discord.PartialReactionEmoji emoji:
        :param int message_id:
        :param int channel_id:
        :param int user_id:
        :return:
        """
        if emoji.is_custom_emoji():
            emoji_id = emoji.id
        else:
            emoji_id = emoji.name

        has_reactrole, combos = await self.has_reactrole_combo(message_id, emoji_id)

        if not has_reactrole:
            return

        try:
            member = self._get_member(channel_id, user_id)
        except LookupError:
            return

        if member.bot:
            return

        try:
            roles = [self._get_role(member.guild, c.role_id) for c in combos]
        except LookupError:
            return

        try:
            await member.add_roles(*roles)
        except discord.Forbidden:
            pass

    async def on_raw_reaction_remove(self, emoji: discord.PartialReactionEmoji,
                                     message_id: int, channel_id: int, user_id: int):
        """
        Event handler for long term reaction watching.

        :param discord.PartialReactionEmoji emoji:
        :param int message_id:
        :param int channel_id:
        :param int user_id:
        :return:
        """
        if emoji.is_custom_emoji():
            emoji_id = emoji.id
        else:
            emoji_id = emoji.name

        has_reactrole, combos = await self.has_reactrole_combo(message_id, emoji_id)

        if not has_reactrole:
            return

        try:
            member = self._get_member(channel_id, user_id)
        except LookupError:
            return

        if member.bot:
            return

        try:
            roles = [self._get_role(member.guild, c.role_id) for c in combos]
        except LookupError:
            return

        try:
            await member.remove_roles(*roles)
        except discord.Forbidden:
            pass
