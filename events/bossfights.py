
# Red
from redbot.core import Config, bank, commands, checks
from redbot.core.data_manager import bundled_data_path

# Standard Library
import asyncio
import csv
import logging
import random
import textwrap
import uuid
from bisect import bisect
from copy import deepcopy
from itertools import zip_longest

# BOSSFIGHTS
import io
import aiohttp
import datetime


# Discord.py
import discord

# Red
from redbot.core import Config, bank, commands
from redbot.core.data_manager import bundled_data_path

        
class BossFights:
    
        
    def __init__(self, ctx, bot, config):
        self.ctx = ctx  
        self.bot = bot
        self.config = config
        
    async def start_fight(self):
    
        boss_name = 'Cromulon'
        weakness_emoji = "🎵"
        weapon_emoji = "🎷"
        reaction_emojis =["🔥","🎵",':portalgun:476677798719913987',":firesword:476664127188893696"]
        
        start_message = "**A {} has spawned! Defeat it before it escapes!**".format(boss_name)
        weakness_message = "**Weakness:** {} \n__A {} will deal extra damage to it!__".format(weakness_emoji, weapon_emoji)
        
        # Posts the "Boss Fight" title, an image of the boss as well as a message.
        async with aiohttp.ClientSession() as session:
            async with session.get('https://i.imgur.com/j560Rjv.png') as resp:
                if resp.status != 200:
                    return await channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await self.ctx.send(file=discord.File(data, 'gyJJwxp.png'))
                
                
      
        
            async with session.get('http://i.imgur.com/jBwJzeu.png') as resp:
                if resp.status != 200:
                    return await channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                message = await self.ctx.send(start_message,file=discord.File(data, '6nSCPQK.png'))
        
        # Announces weakness
        await  self.ctx.send(weakness_message)
          
        # Adds reactions.
        for i in reaction_emojis:
                    await message.add_reaction(i)
        

        # LOVE THIS
        
        caught_reactions = list()
        reactusers = list()

        begin = datetime.datetime.now()
        current = begin

        m = message

        def ch(r, u):
            return r.message.id == m.id and self.bot.user != u

        timeout_value = 4
        damagecounter = 0
        damageweapon = "Fire Sword"

        try:
            while (damagecounter < 2) or ((current - begin).seconds > timeout_value):
            
                current = datetime.datetime.now()
                
                
                reaction, user = await self.bot.wait_for('reaction_add',
                                              timeout=(timeout_value - (current-begin).seconds),
                                              check=ch)
                    
            
                # THIS CODE RUNS IF THE REACTION IS ACTUALLY GONNA BE DONE SOMETHING WITH.
                if user not in reactusers:
                    reactusers.append(user)
                    damagecounter += 1
                    # customitems = ctx.bot.get_cog('CustomItems')
                    shop = self.ctx.bot.get_cog('Shop')
                    inventory = await shop.inv_hook(user)
                    item = damageweapon
                    if data is None:
                        continue
                    if(inventory['Fire Sword']['Qty'] >= 1):
                        damagecounter += 1
                            
                    
                    
                    
            await self.ctx.send("You beat the boss!")
        
        except asyncio.TimeoutError:
            await self.ctx.send("The boss escaped!")
            
        
        
        
        
        
        
        
        
        
        
        
        """
        async def reaction_waity():
        
        
        
            print("START")
            counter = 0
            reactionset = set()
            
            while(counter<1):
                (reaction, user) = await self.ctx.bot.wait_for('reaction_add')
                
                print("reaction")
                print(reaction)
                print("weapon_reaction")
                print(weapon_emoji)
                
                if str(reaction.emoji) == str(weapon_emoji):
                    weapon = "Fire Sword"
                    
                    #customitems = ctx.bot.get_cog('CustomItems')
                    instance = self.config.member(user)
                    data = await instance.Inventory.all()
                    if data is None:
                        return await ctx.send("NONE")
                    if item not in data:
                        return await ctx.send("You don't own this item.")
                    
                    
                    reactionset.add(user)
                    print("This is reactionlist:")
                    print(reactionset)
                    counter = counter + 1
            
            
            return reactionset
            
        
        
        try:    
        print("DID WE MAKE IT")
        await self.ctx.bot.wait_for('reaction_waity()', timeout=5, check=check)
        print("DASDASDASDS")
        #customitems = ctx.bot.get_cog('CustomItems')
        #await customitems.redeem_item(ctx, item)
        except asyncio.TimeoutError:
            print("We in here!")"""
           
        
    
        
                   
    
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        