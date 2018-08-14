import discord
from discord.ext import commands
from discord import client
from redbot.core import Config, bank
import asyncio

class leaderboard:

    def __init__(self, bot):
        print('Loaded Leaderboard')
        self.leaderboard_message = None
        self.last_leaderboard = None
        self.bot = bot

        self.bot.loop.create_task(self.update_leaderboard())


    """
    updates the leaderboard by either making a new message if none exists or editing an existing message

    high level overview of the loop:

        1). if we havent before, check messages in a given channel and find the most recent message sent from our bot
            a.) if no message is found we send a message and use that
        2). we use a function ripped from economy to format the leaderboard
        3.) we make sure that this leaderboard is different than the last one we got
        4.) we try to edit the message found in #1 with the leaderboard data
            a.) if this fails, force the next iteration of the loop to find a new message

    """
    #@commands.command()
    async def update_leaderboard(self):
        while self == self.bot.get_cog('Leaderboard'):

            #gets a message so we can edit it
            if self.leaderboard_message == None:
                channel = self.bot.get_channel(474801276408954891)

                async for message in channel.history(limit=5):
                    if message.author.id == 474030873742671892:
                        self.leaderboard_message = message
                        break
                else:
                    self.leaderboard_message = await channel.send('Loading leaderboard...')


            ctx = self.leaderboard_message

            leaderboard = await self._leaderboard(ctx)


            #if the leaderboard has changed since last loop
            if self.last_leaderboard != leaderboard:
                self.last_leaderboard = leaderboard

                if self.leaderboard_message == None:
                    #make sure we have a message we can edit (weird edgecase)
                    await self.channel.send(leaderboard)
                else:
                    try: 
                        await self.leaderboard_message.edit(content=str(leaderboard))
                    except (discord.NotFound, discord.errors.NotFound, discord.HTTPException):
                        #if the message is deleted, force a check for a new message
                        self.leaderboard_message = None
                        self.last_leaderboard = None


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