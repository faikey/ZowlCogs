
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
from collections import Counter

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
        self.commandschannel = discord.utils.get(ctx.guild.channels,id=482700648635301931)
        

        bf_defaults = {
            # Doesn't work atm
                "Weakness_Multiplier": 2.5
        }

        self.config.register_guild(**bf_defaults)
        
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
        boss_uptime = 60
        
        # Gets commands channel mention thing.
        commandsmention = self.commandschannel.mention
        # Makes the role pingable, then unpingable.
        # FIX THIS
        role =  discord.utils.get(self.ctx.guild.roles,id=477656812997312514)
        await role.edit(mentionable=True)
        start_message = "<@&477656812997312514>\n**A {} with **{} HP** has spawned! Defeat it in __{}__ seconds or it will escape!**\nEquip any weapons in {}!".format(boss_name, hp, boss_uptime, commandsmention)
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
        # A list of all users who has dealt damage.
        participating_users = []
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
        
        def ch1(r, u): # Checks - check()
            return self.bot.user != u and r.message.id == bossmessage.id

        def ch2(m):
            return self.bot.user != m.author and (m.channel == self.channel or m.channel == self.commandschannel)


        try:
            while (currenthp != 0) or ((current - begin).seconds > timeout_value):
            
                current = datetime.datetime.now()
                timer = timeout_value - (current - begin).seconds

                # Put this inside a while loop, like the timed one from trivia or wherever. The guy who helped.
                # tasks = [self.bot.wait_for(event) for event in ['reaction_add', 'message']]
                tasks = [self.ctx.bot.wait_for('message', check=ch2),
                        self.ctx.bot.wait_for('reaction_add', check=ch1)]
                
                done, left = await asyncio.wait(tasks, timeout=timer, return_when=asyncio.FIRST_COMPLETED)

                [task.cancel() for task in left]
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
                                    #weaknessmultiplier = await self.config.guild(self.ctx.guild).Weakness_Multiplier.all()
                                    weaknessmultiplier = 1.5
                                    weaknessflatrate = 2
                                    turndamagecounter = (turndamagecounter*weaknessmultiplier)+weaknessflatrate
                                    users_damage[user.id] = int(turndamagecounter)
                            except KeyError:
                                damage_type = ""

                            turndamagecounter = int(turndamagecounter)
                            currenthp -= turndamagecounter
                            currenthp = currenthp

                            if currenthp < 0:
                                currenthp = 0
                            
                            dealtdmgmsg = await self.user_dealt_damage(user, turndamagecounter, damage_type, currenthp)
                            participating_users.append(user.id)
                            remove_messages.append(dealtdmgmsg)
                            currenthp = currenthp


                    # IF THE INPUT IS A MESSAGE
                    else:
                        message = result  # is a message    
                        """try:
                            await message.delete()
                        except discord.errors.NotFound:
                            print("We didn't delete the message, sorry!")"""
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

                                                    currentdamagenow, user_damage_type, combodelmsgs = await self.weapon_use(user, data, weaponname, weapondata, weaponsused, currentdamage)
                                                    
                                                    remove_messages.extend(combodelmsgs)
                                                    users_damage[user.id] = currentdamagenow
                                                    users_damage_type[user.id] = user_damage_type
                                                    users_weaponsused[user.id] = weaponsused[user.id]
                                                    
                

            ### END SHIT, AFTER WHILE LOOP
            # Coins image
            
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
                        moneymessage = await self.channel.send(file=discord.File(data, 'sqEqgZa.png'))

                finalmsg = await self.channel.send("**VICTORY!**\nYou beat the boss!")
                msglist = await self.give_loot(users_damage, hp)
                # Removes all "LOLOL DMG DEALT" messages and stuff.
                for message in remove_messages:
                    await message.delete()
                # Increases users boss participation.
                self.gconf = self.config.guild(self.ctx.guild)
                for userid in participating_users:
                    try:
                        #bosscounter = await self.gconf.get_raw('bossfights', userid, 'Kills')
                        bosscounter = await self.gconf.get_raw('users', userid, 'bossfights', 'Kills')
                        bosscounter += 1
                    except KeyError:
                        bosscounter = 1
                    await self.gconf.set_raw('users', userid, 'bossfights', 'Kills', value=bosscounter)

                await asyncio.sleep(10)
                for m in msglist:
                    await m.delete()
                await moneymessage.delete()
                await finalmsg.delete()
                await victorymessage.delete()

            else:
                
                nospamdel = await self.channel.send("**The boss escaped!**")
                for m in remove_messages:
                    await m.delete()
                await asyncio.sleep(12)
                await nospamdel.delete()

        except KeyError:
            pass


    async def user_dealt_damage(self, user, damage, damagetype, currenthp):
            mention = user.mention
            message = await self.channel.send("{} dealt **{}** {} damage to the boss! Boss HP: {}".format(mention, damage, damagetype, currenthp))
            return message
        
        
    async def give_loot(self, users_damage, hp):
        msglist = []
        for userid, damage in users_damage.items():
            damage = int(damage)
            #self.gconf = self.config.guild(self.ctx.guild)
            user = self.ctx.guild.get_member(userid)
            money = (damage * 2.4) * random.uniform(0.8,1.8)
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
        currentdamage += weapondata["Damage"]
        damagetype = weapondata["Type"]
        combodelmsgs = []

        equipmsg = await self.channel.send("{} has equipped a {} and acquired {} damage!".format(user.mention, weapondata["Emoji"], damagetype))
        # We might want to tell what weapons were used to make x damage later. Not now.
        combodelmsgs.append(equipmsg)
        
        try:
            templist = weaponsused[user.id]
            templist.append(weapondata)
            weaponsused[user.id] = templist
        except KeyError: 
            templist = list()
            templist.append(weapondata)
            weaponsused[user.id] = templist

        combochecklist = list()
        for key, value in weaponsused.items():
            for weapon in value:
                combochecklist.append(weapon["Type"])
            lenclaus = len(templist)

        def find_combo(input, combos):
            for combolist in combos:
                if set(input) == set(combolist[:2]):
                    return combolist[2]
            return None

        if lenclaus > 1:
            currentdamage += 2
            combos = data["damage_info"]["Combos"]
            combotype = find_combo(combochecklist, combos)
            if combotype is not None:
                    currentdamage += 2
                    damagetype = combotype
                    combodelmsg = await self.channel.send("{} has created {} damage!".format(user.mention,damagetype))
                    combodelmsgs.append(combodelmsg)
            
        # Handles weapon charges.
        base_charges = data["base_values"]["Charges"]
        await self.use_charge(user, weaponname,base_charges)
        #print("Wepon used I ugess?")
        return currentdamage, damagetype, combodelmsgs


    # Initiates people's inventory with 4 charges. Uses one upon initiating.
    async def use_charge(self, user, weaponname, base_charges):
        shop = self.ctx.bot.get_cog('Shop')
        

        currchargedict = await shop.get_attr(self.ctx, user, weaponname, ['charges'])
        currcharge = currchargedict['charges']
        #print(currcharge)
        if  currcharge is None: 
            updated_charges = base_charges-1
            await shop.set_attr(self.ctx,user,weaponname,{'charges':updated_charges})
        elif currcharge == 1:
            await shop.item_remove(self.ctx, weaponname)
        else:
            await shop.update_attr(self.ctx,user,weaponname,{'charges':-1})

            