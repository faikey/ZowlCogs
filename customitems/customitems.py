import discord
from discord.ext import commands
from redbot.core import bank
from redbot.core import Config
import random

class CustomItems:
    """My custom cog"""
 
    
    def __init__(self):
        self.config = Config.get_conf('Shop', identifier=5074395003, force_registration=True)
        
    
    @commands.command()
    async def mycom(self, ctx):
        # Your code will go here
        await ctx.send("I can do stuff!")

    async def redeem_item(self, ctx, item):
        if(item == 'Gold Bar'):
            await self.redeem_goldbar(ctx, item)
        elif('Safe' in item):
            await self.redeem_safe(ctx, item)
        else:
            ctx.send("Sorry, can't redeem that item!")
    
    async def redeem_goldbar(self, ctx, item):
        await ctx.send("You don't have a gold bar!")
        print('callback')
        print(ctx)
        shop = ctx.bot.get_cog('Shop')
        inventory = await shop.inv_hook(ctx.author)
        author = ctx.author
        """Converts gold item to credits."""
        try:
            if (inventory['Gold Bar']['Qty'] >= 1):
                """Removes gold bar."""
                """insert remove here"""
                await shop.item_remove(ctx, 'Gold Bar')
                currency = await bank.get_currency_name(ctx.guild)
                bal = await bank.get_balance(author)
                goldworth = 100
                newbal = bal + goldworth
                
                await bank.set_balance(author, newbal)
                await ctx.send("You traded a Gold bar for {} {}! \nYou now have {} {}!".format(goldworth,currency,newbal,currency))
        except AttributeError:
            await ctx.send("You don't have a gold bar!")
        except KeyError:
            await ctx.send("You don't have a gold bar!")
            
    async def redeem_safe(self, ctx, item):  
        user = ctx.author
        rob = ctx.bot.get_cog('Rob')
        shop = ctx.bot.get_cog('Shop')
        safes = ('Blue', 'Yellow', 'Red')
        
        await ctx.send(safes[0])
        
        if(safes[0] in item):
            await rob.rob_def_increase(ctx, 0.1)
        if(safes[0] in item):
            await rob.rob_def_increase(ctx, 0.2)
        if(safes[0] in item):
            await rob.rob_def_increase(ctx, 0.3)
            
        await shop.item_remove(ctx, item)
            
    
    async def setbalance(self, ctx):
        try:
            economy = ctx.bot.get_cog('Economy')
            await bank.leaderboardchannel(474801276408954891)
        except KeyError:
            await ctx.send("Leaderboard won't update.")