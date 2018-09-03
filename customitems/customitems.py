import discord
from discord.ext import commands
from redbot.core import bank
from redbot.core import Config
import time
import random

class CustomItems:
    """My custom cog"""
    
     
    
    def __init__(self):
        self.config = Config.get_conf(self, identifier=8358350001, force_registration=True)
        
        items = {"items":{
        "Gold_Bar": 100,
        "Safe":{
            "Cooldown": 345600,
            "Colors":{
                "Blue": 0.1,
                "Yellow": 0.14,
                "Red": 0.18}
                }
            }
        }
        
        self.config.register_guild(**items)
        
        

    async def redeem_item(self, ctx, item):
        self.gconf = self.config.guild(ctx.guild)
        
        if(item == 'Gold Bar'):
            await self.redeem_goldbar(ctx, item)
        elif('Safe' in item):
            await self.redeem_safe(ctx, item)
        else:
            await ctx.send("Sorry, can't redeem that item!")
    
    async def redeem_goldbar(self, ctx, item):
        self.gconf = self.config.guild(ctx.guild)
        
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
                goldworth = await self.gconf.get_raw('items', 'Gold_Bar')
                newbal = int(bal + goldworth)
                
                await bank.set_balance(author, newbal)
                await ctx.send("You traded a Gold bar for {} {}! \nYou now have {} {}!".format(goldworth,currency,newbal,currency))
        except AttributeError:
            await ctx.send("You don't have a gold bar!")
        except KeyError:
            await ctx.send("You don't have a gold bar!")
            
    async def redeem_safe(self, ctx, item): 
        
        safestr = " Safe"
        self.gconf = self.config.guild(ctx.guild)
        user = ctx.author
        rob = ctx.bot.get_cog('Rob')
        shop = ctx.bot.get_cog('Shop')
       
        # Gets the safe color, uses it to find the safe value, increases user's Rob Defense.
        safe_colors = await self.gconf.get_raw('items', 'Safe', 'Colors')
        item_color = item.split(' ')[0]
        if(item_color not in safe_colors):
            return await ctx.send("That safe color doesn't exist here! Scream, weirdo!")
        
        #Increases rob defense.
        value = safe_colors[item_color]
        canincrease = await rob.rob_def_increase(ctx, value)
        
        if canincrease:
            await shop.item_remove(ctx, item)
            await ctx.send("*This bonus will last for **3** days.*")
            
    
    async def setbalance(self, ctx):
        try:
            economy = ctx.bot.get_cog('Economy')
            # await bank.leaderboardchannel(474801276408954891)
        except KeyError:
            await ctx.send("Leaderboard won't update.")

    async def get_charges(self, ctx, user, item):
        pass
        """shop = ctx.bot.get_cog('Shop')
        inventory = await shop.inv_hook(user)
        try:
            charges = inventory[item]['Charges']
            return charges
        except KeyError:
            inventory[item]['Charges'] = 3
            return 3"""

    async def use_charge(self, ctx, user, item):
        pass
        """if self.get_charges(ctx, user, item) == 1:
            item.remove
        else:
            shop = ctx.bot.get_cog('Shop')
            inventory = await shop.inv_hook(user)"""

        # if 0, remove item
