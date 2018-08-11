import discord
from discord.ext import commands
from redbot.core import Config, bank
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

class Leaderboard:



    def __init__(self):
        print('Loaded Leaderboard')


    @commands.command()
    async def leaderboardTest(self, ctx: commands.Context, top: int = 10, show_global: bool = False):
        """Prints out the leaderboard

        Defaults to top 10"""
        guild = ctx.guild
        author = ctx.author
        if top < 1:
            top = 10
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
            await menu(ctx, pages, DEFAULT_CONTROLS)
        else:
            await ctx.send("There are no accounts in the bank.")


    async def update(self, ctx, leaderboard):
        pass
    #edit message here




    @commands.command()
    #@commands.cooldown(rate=1, per=14400, type=discord.ext.commands.BucketType.user)
    async def ll(self, ctx):
        economy = ctx.bot.get_cog('Economy') #its actually just bank you named the test cog wrong
        economy.leaderboard_pass(ctx, 10, True)

    