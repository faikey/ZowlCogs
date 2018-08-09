import discord
from discord.ext import commands
from redbot.core import Config, bank

class Leaderboard:



    def __init__(self):
        print('Loaded Leaderboard')



    async def update(self, ctx, leaderboard):
        pass
    #edit message here




    @commands.command()
    #@commands.cooldown(rate=1, per=14400, type=discord.ext.commands.BucketType.user)
    async def ll(self, ctx):
        economy = ctx.bot.get_cog('Economy') #its actually just bank you named the test cog wrong
        print(economy)

    