import discord
from discord.ext import commands
from discord import client
from redbot.core import Config, bank
import asyncio

from collections import OrderedDict

class Leaderboard:

    def __init__(self, bot):
        print('Loaded Leaderboard')
        self.boss_last_leaderboard = None
        self.last_leaderboard = None
        self.bot = bot

        self.bot.loop.create_task(self.update_leaderboard())
        self.bot.loop.create_task(self.update_boss_leaderboard())




    """
    sends and handles updates for boss leaderboard
    """
    async def update_boss_leaderboard(self):
        while self == self.bot.get_cog('Leaderboard'):

            channel = self.bot.get_channel(474801276408954891)
            message = await channel.get_message(482319441192026146)

            leaderboard = await self._boss_leaderboard()

            if self.boss_last_leaderboard != leaderboard:
                await message.edit(content=str(leaderboard))
                self.boss_last_leaderboard = Leaderboard

            await asyncio.sleep(5)


    """
    generates message for boss leaderboard
    """
    async def _boss_leaderboard(self):
        boss = self.bot.get_cog('Events')
        stats = await boss.get_boss_kills(278639962558300160)
        unsorted_board = {}

        # re format board so we can sort it
        for user, value in stats.items():
            unsorted_board[user] = int(value['bossfights']['kills'])

        sorted_board = sorted(OrderedDict(unsorted_board).items(), key=lambda x:-x[1])

        # create leaderboard
        leaderboard_message = "```md\n" + f"{f'#':4}{f'Name':36}{f'Boss Kills':2}\n"
        for i, d in enumerate(sorted_board):
            user = self.bot.get_user(int(d[0])).name
            leaderboard_message = leaderboard_message + f"{f''+str(i+1)+'.':4}{f''+user:36}{f''+str(d[1]):2}\n"
        leaderboard_message = leaderboard_message + '```'

        return leaderboard_message



    """
    updates the leaderboard by either making a new message if none exists or editing an existing message
    """
    async def update_leaderboard(self):
        while self == self.bot.get_cog('Leaderboard'):

            channel = self.bot.get_channel(474801276408954891)
            message = await channel.get_message(482081766274891796)

            leaderboard = await self._leaderboard(message)

            if self.last_leaderboard != leaderboard:
                await message.edit(content=str(leaderboard))
                self.last_leaderboard = Leaderboard

            await asyncio.sleep(5)



    """
    taken from the economy cog (https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/economy/economy.py#L309) 

    Arguments:
        ctx: d.py message object that we can derive the guild from

    Returns:
        leaderboard in text form
    """
    async def _leaderboard(self, ctx):
        top = 10
        show_global = False


        guild = ctx.guild
        if (
            await bank.is_global() and show_global
        ):  # show_global is only applicable if bank is global
            guild = None
        bank_sorted = await bank.get_leaderboard(positions=top, guild=guild)
        if len(bank_sorted) < top:
            top = len(bank_sorted)
        header = f"{f'#':4}{f'Name':36}{f'Score':2}\n"
        highscores = [
            (
                f"{f'{pos}.': <{3 if pos < 10 else 2}} {acc[1]['name']: <{35}s} "
                f"{acc[1]['balance']: >{2 if pos < 10 else 1}}\n"
            )
            for pos, acc in enumerate(bank_sorted, 1)
        ]
        if highscores:
            pages = [
                f"```md\n{header}{''.join(''.join(highscores[x:x + 10]))}```"
                for x in range(0, len(highscores), 10)
            ]

            return pages[0]

            