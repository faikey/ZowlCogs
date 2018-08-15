
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
import json
import math

# BOSSFIGHTS
import io
import aiohttp
import datetime


# Discord.py
import discord
from discord.ext import commands

# Red
from redbot.core import Config, bank, commands, checks
from redbot.core.data_manager import bundled_data_path

        
class BossFights:
    
        
    def __init__(self, ctx, bot, config, data, channel):
        self.ctx = ctx  
        self.bot = bot
        self.config = config
        self.data = data
        self.channel = channel


        #self.config.register_guild(**event_defaults)

    
    """async def import_json(self): 
        path = bundled_data_path(self) / 'data.json'
        print(path)
        with open(path) as f:
            data = json.load(f)

        return data"""
        
    async def start_fight(self):

        # Import data from json. 
        data = self.data

        # Chooses a random boss.
        bossnamelist = list()
        for bossname in data["bosses"].keys():
            bossnamelist.append(bossname)
        bossname = random.choice(bossnamelist)
        bossdict = data["bosses"][bossname]

        boss_name = bossname
        hp = bossdict["HP"]
        weakness = bossdict["Weakness"]
        bonus_type = bossdict["Bonus_Type"]
        link = bossdict["Link"]
        filenamelist = link.split("/")
        filename = filenamelist[3]

        # Constants
        reaction_emojis =["🔥","🍃","💨","💧"]
        boss_uptime = 30
        
        # Makes the role pingable, then unpingable.
        role =  discord.utils.get(self.ctx.guild.roles,id=477656812997312514)
        await role.edit(mentionable=True)
        start_message = "<@&477656812997312514>\n**A {} has spawned! Defeat it in __{}__ seconds or it will escape!**".format(boss_name,boss_uptime)
        await role.edit(mentionable=False)

        weakness_message = "**Weakness:** {}".format(weakness)
        
        # Posts the "Boss Fight" title, an image of the boss as well as a message.
        async with aiohttp.ClientSession() as session:
            async with session.get('https://i.imgur.com/j560Rjv.png') as resp:
                if resp.status != 200:
                    return await self.channel.send('Could not download file...')
                dldata = io.BytesIO(await resp.read())
                imgtitle = await self.channel.send(file=discord.File(dldata, 'gyJJwxp.png'))



            # Boss image and text
            async with session.get(str(link)) as resp:
                if resp.status != 200:
                    return await self.channel.send('Could not download file...')
                dldata = io.BytesIO(await resp.read())
                message = await self.channel.send(start_message,file=discord.File(dldata, str(filename)))
        
        # Announces weakness
        weaknessmsg = await self.channel.send(weakness_message)
          
        # Adds reactions.
        for i in reaction_emojis:
                    await message.add_reaction(i)
        

        # LOVE THIS
        # IF SHIT DOESN'T RUN IT'S BECAUSE ROLE ID THING AND CHANNEL ID!!! JARLE
        
        caught_reactions = list()
        reactusers = list()
        # The timestamp which the bossfight starts.
        begin = datetime.datetime.now()
        current = begin
        bossmessage = message
        # How long tha boss is alive.
        timeout_value = boss_uptime
        # Collected damage counter.
        damagecounter = 0
        # Boss' hp over the course of the battle
        currenthp = hp
        # Which weapon deals extra damage to the boss.
        damageweapon = "Fire Sword"
        # A dict that keeps track of how much damage each user has dealt. Returns a KeyError if the user hasn't increased his damage any way.
        users_damage = {}
        # Keeps track of which damage type the current user has. Returns a KeyError if the user has no damage type.
        users_damage_type = {}
        # Which messages to remove once the bossfight is finished.
        remove_messages = [message, imgtitle, weaknessmsg]
        # Stores each user's weapon's used over the bossfight.
        users_weaponsused = {}
        
        # Shop cog for inventory use.
        shop = self.bot.get_cog('Shop')
        
        #
        weaponemojis = []
        for weaponname, weapondata in data['items'].items():
            for key, value in weapondata.items():
                if key=="Emoji":
                    weaponemojis.append(value)

        # WAITS FOR REACTION OR MESSAGE.
        
        def ch1(r, u):
            return self.bot.user != u and r.message.id == bossmessage.id

        def ch2(m):
            return self.bot.user != m.author and m.channel == self.channel

        try:
            while (currenthp != 0) or ((current - begin).seconds > timeout_value):
            
                current = datetime.datetime.now()
                timer = timeout_value - (current - begin).seconds
                print(timer)

                # Put this inside a while loop, like the timed one from trivia or wherever. The guy who helped.
                # tasks = [self.bot.wait_for(event) for event in ['reaction_add', 'message']]
                tasks = [self.ctx.bot.wait_for('message', check=ch2),
                        self.ctx.bot.wait_for('reaction_add', check=ch1)]
                
                done, left = await asyncio.wait(tasks, timeout=timer, return_when=asyncio.FIRST_COMPLETED)

                [task.cancel() for task in left]
                print("We got here?")
                try:
                    result = done.pop().result()
                except KeyError:
                    break
                else:
                    if isinstance(result, tuple):
                        reaction, user = result  # is a reaction_add or reaction_remove
                        if user not in reactusers:
                            reactusers.append(user)
                            # Checks if the user reacted to the bonus type. DISABLED ATM
                            bonus = False
                            # Starts counting how much damage the user will deal on the reaction. This value is added onto "damagecounter" at the end.
                            turndamagecounter = 0
                            
                            # Checks if the reaction is the bonus type.
                            if(reaction.emoji == bonus_type):
                                turndamagecounter += 1
                                #bonus = True

                            try:
                                item_damage = users_damage[user.id]
                                turndamagecounter += item_damage
                            except KeyError:
                                turndamagecounter += 1
                            # Tries to see if the user has any damage types.
                            try:
                                damage_type = users_damage_type[user.id]
                                if damage_type == weakness:
                                    turndamagecounter = turndamagecounter*1.5
                                    users_damage[user.id] = turndamagecounter
                            except KeyError:
                                damage_type = ""

                            turndamagecounter = int(turndamagecounter)
                            currenthp -= turndamagecounter
                            currenthp = currenthp

                            if currenthp < 0:
                                currenthp = 0
                            
                            msg = await self.user_dealt_damage(user, turndamagecounter, damage_type, currenthp)
                            currenthp = currenthp


                    # IF THE INPUT IS A MESSAGE
                    else:
                        message = result  # is a message
                        try:
                            await message.delete()
                        except discord.errors.NotFound:
                            pass
                        # This part of the code takes a user's message, and checks if the message - an emoji - is a weapon.
                        emoji = message.content
                        user = message.author
                        nrweaponsused = 0

                        try:
                            nrweaponsused = len(users_weaponsused[user.id])
                        except KeyError:
                            pass

                        if nrweaponsused < 2:
                            if emoji in weaponemojis:
                                for weaponname, weapondata in data['items'].items():
                                    for key, value in weapondata.items():
                                        if key == 'Emoji':
                                            if value == emoji:
                                                inventory = await shop.inv_hook(message.author)
                                                if weaponname in inventory:
                                                    currentdamage = 1
                                                    try:
                                                        currentdamage = users_damage[user.id]
                                                    except KeyError:
                                                        weaponsused = dict()

                                                    currentdamagenow, user_damage_type = await self.weapon_use(user, data, weaponname, weapondata, weaponsused, currentdamage)
                                                    print(currentdamagenow)
                                                    users_damage[user.id] = currentdamagenow
                                                    users_damage_type[user.id] = user_damage_type
                                                    users_weaponsused[user.id] = weaponsused[user.id]
                                                    #currenthp -= currentdamage
                                                    print("We got here somehow")
                                                    
                

            ### END SHIT, AFTER WHILE LOOP
            # Coins image
            for m in remove_messages:
                    await m.delete()
            if currenthp == 0:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://i.imgur.com/bs2flp4.png') as resp:
                        if resp.status != 200:
                            return await self.channel.send('Could not download file...')
                        data = io.BytesIO(await resp.read())
                        victorymessage = await self.channel.send(file=discord.File(data, 'bs2flp4.png'))

                # Coins image
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://i.imgur.com/sqEqgZa.png') as resp:
                        if resp.status != 200:
                            return await self.channel.send('Could not download file...')
                        data = io.BytesIO(await resp.read())
                        moneymessage = await self.ctx.send(file=discord.File(data, 'sqEqgZa.png'))

                finalmsg = await self.channel.send("**VICTORY!**\nYou beat the boss!")
                msglist = await self.give_loot(users_damage, hp)
                
                await asyncio.sleep(10)
                for m in msglist:
                    await m.delete()
                await moneymessage.delete()
                await finalmsg.delete()
                await victorymessage.delete()

            else:
                await self.channel.send("**The boss escaped!**")

        except KeyError:
            pass


    async def user_dealt_damage(self, user, damage, damagetype, currenthp):
            mention = user.mention
            message = await self.channel.send("{} dealt **{}** {} damage to the boss! Boss HP: {}".format(mention, damage, damagetype, currenthp))
            return message
        
        
    async def give_loot(self, users_damage, hp):
        msglist = []
        print(users_damage)
        for userid, damage in users_damage.items():
            print("asdasdadwadwd")
            damage = int(damage)
            #self.gconf = self.config.guild(self.ctx.guild)
            user = self.ctx.guild.get_member(userid)
            money = (damage * 3) * random.uniform(0.8,1.8)
            money = int(money)
            currency = await bank.get_currency_name(self.ctx.guild)
            await bank.deposit_credits(user, money)
            msg = await self.channel.send("{} received {} {}!".format(user.mention,money,currency))
            msglist.append(msg)
            await asyncio.sleep(1)

        return msglist
    
    # This adds the weapons damage and also accomodates for combos. One can also not equip more than 2 weapons.

    async def weapon_use(self, user, data, weaponname, weapondata, weaponsused, currentdamage):

        # The method assumes that the user has the item, and that it has charges.
        customitems = self.bot.get_cog("CustomItems")
        print("To current damage")
        print(currentdamage)
        currentdamage += weapondata["Damage"]
        print(currentdamage)
        damagetype = weapondata["Type"]
        print(damagetype)
    
        equipmsg = await self.channel.send("{} has equipped a {}!".format(user.mention, weapondata["Emoji"]))
        # We might want to tell what weapons were used to make x damage later. Not now.
        
        try:
            templist = weaponsused[user.id]
            templist.append(weapondata)
            weaponsused[user.id] = templist
            print("The try succeeded")
            print(templist)
        except KeyError: 
            templist = list()
            templist.append(weapondata)
            weaponsused[user.id] = templist
            print("The try failed")
            print(weaponsused)

        combochecklist = list()
        for key, value in weaponsused.items():
            for weapon in value:
                print(key)
                print("CHECKLIST APPEND")
                combochecklist.append(weapon["Type"])
                print(weapon["Type"])
            lenclaus = len(templist)

        
        if lenclaus > 1:
            combos = data["damage_info"]["Combos"]
            for combolist in combos:
                if all(elem in combolist for elem in combochecklist):
                    damagetype = combolist[2]
                    await self.channel.send("{} has created {} damage!".format(user.mention,damagetype))

        #await customitems.use_charge(self.ctx, user, weapon)
        return currentdamage, damagetype
