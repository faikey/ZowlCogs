
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


        #self.config.register_guild(**event_defaults)
        
    async def start_fight(self):


        boss_name = 'Cromulon'
        weakness_emoji = "🎵"
        weapon_emoji = "🎷"
        reaction_emojis =["🔥","🍃","💨","❄"]
        boss_uptime = 30
        
        start_message = "**A {} has spawned! Defeat it in __{}__ seconds or it will escape!**".format(boss_name,boss_uptime)
        weakness_message = "**Weakness:** {} \n__A {} will deal extra damage to it!__".format(weakness_emoji, weapon_emoji)
        
        # Posts the "Boss Fight" title, an image of the boss as well as a message.
        async with aiohttp.ClientSession() as session:
            async with session.get('https://i.imgur.com/j560Rjv.png') as resp:
                if resp.status != 200:
                    return await self.ctx.channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                imgtitle = await self.ctx.send(file=discord.File(data, 'gyJJwxp.png'))



            # Boss image and text
            async with session.get('http://i.imgur.com/jBwJzeu.png') as resp:
                if resp.status != 200:
                    return await self.ctx.channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                message = await self.ctx.send(start_message,file=discord.File(data, '6nSCPQK.png'))
        
        # Announces weakness
        weaknessmsg = await self.ctx.send(weakness_message)
          
        # Adds reactions.
        for i in reaction_emojis:
                    await message.add_reaction(i)
        

        # LOVE THIS
        
        caught_reactions = list()
        reactusers = list()
        # The timestamp which the bossfight starts.
        begin = datetime.datetime.now()
        current = begin
        m = message
        # How long tha boss is alive.
        timeout_value = boss_uptime
        # Collected damage counter.
        damagecounter = 0
        # Lol
        viableitems = 2
        # Boss hp
        hp = 2
        # Boss' hp over the course of the battle
        currenthp = hp
        # Which weapon deals extra damage to the boss.
        damageweapon = "Fire Sword"
        # A dict that keeps track of how much damage each user has dealt.
        users_damage = {}
        # Which messages to remove once the bossfight is finished.
        remove_messages = []

        async def endfunction():
            await message.delete()
            await weaknessmsg.delete()
            
        
        def ch(r, u):
            return r.message.id == m.id and self.bot.user != u

        try:
            while (damagecounter < hp) or ((current - begin).seconds > timeout_value):
            
                current = datetime.datetime.now()
                
                
                reaction, user = await self.bot.wait_for('reaction_add',
                                              timeout=(timeout_value - (current-begin).seconds),
                                              check=ch)
                    
            
                # THIS CODE RUNS IF THE REACTION IS ACTUALLY GONNA BE DONE SOMETHING WITH.
                if user not in reactusers:
                    
                    itemused = None
                    reactusers.append(user)
                    damagecounter += 1
                    turndamagecounter = 1
                    # customitems = ctx.bot.get_cog('CustomItems')
                    shop = self.ctx.bot.get_cog('Shop')
                    inventory = await shop.inv_hook(user)
                    item = damageweapon
                    if data is None:
                        continue
                        
                    whilecounter = 0
                    while(whilecounter < viableitems):
                        try:
                            if whilecounter == 1:
                                if(inventory['Fire Sword']['Qty'] >= 1):
                                    damagecounter += 1
                                    turndamagecounter += 1
                                    itemused = 'Fire Sword'
                                    break
                            elif(inventory['Saxophone']['Qty'] >= 1):
                                damagecounter += 1
                                turndamagecounter += 1
                                itemused = '🎷'
                                break
                        except KeyError:
                            whilecounter += 1
                    
                    currenthp = currenthp - turndamagecounter
                    users_damage[user] = turndamagecounter
                    tempmsg = await self.user_dealt_damage(user, turndamagecounter, currenthp, itemused)
                    remove_messages.append(tempmsg)

            #async for message in self.ctx.history(limit=3, reverse=True):
            #       await message.delete()

            # Coins image
            async with aiohttp.ClientSession() as session:
                async with session.get('https://i.imgur.com/bs2flp4.png') as resp:
                    if resp.status != 200:
                        return await self.ctx.channel.send('Could not download file...')
                    data = io.BytesIO(await resp.read())
                    victorymessage = await self.ctx.send(file=discord.File(data, 'bs2flp4.png'))

            # Coins image
            async with aiohttp.ClientSession() as session:
                async with session.get('https://i.imgur.com/sqEqgZa.png') as resp:
                    if resp.status != 200:
                        return await self.ctx.channel.send('Could not download file...')
                    data = io.BytesIO(await resp.read())
                    moneymessage = await self.ctx.send(file=discord.File(data, 'sqEqgZa.png'))

            finalmsg = await self.ctx.send("**VICTORY!**\nYou beat the boss!")
            await endfunction()
            msglist = await self.give_loot(users_damage, hp)
            remove_messages.extend(msglist)
            await imgtitle.delete()
            await asyncio.sleep(10)
            await moneymessage.delete()
            await finalmsg.delete()
            for message in remove_messages:
                await message.delete()
            await victorymessage.delete()
        
        except asyncio.TimeoutError:

            await self.ctx.send("The boss escaped!")
            await endfunction()
            await asyncio.sleep(10)
            await imgtitle.delete()
        
        
        
        
    async def user_dealt_damage(self, user, damage, currenthp, item=None):
            mention = user.mention
            itemstring = ""
            if item is not None:
                itemstring = " with a {}".format(item)
            message = await self.ctx.send("{} dealt {} damage to the boss{}! Boss HP: {}".format(mention, damage, itemstring, currenthp))
            return message
        
        
    async def give_loot(self, user_dict, hp):
        msglist = []
        for user, damage in user_dict.items():
            money = (damage * 3) * random.randint(1,2)
            currency = await bank.get_currency_name(self.ctx.guild)
            await bank.deposit_credits(user, money)
            msg = await self.ctx.send("{} received {} {}!".format(user.mention,money,currency))
            msglist.append(msg)
            await asyncio.sleep(1)

        return msglist
        
    #sasync def money_calculation(self, damage):
        

        
   
       
    

    
               

            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    