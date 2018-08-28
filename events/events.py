# Discord 
import discord
from discord.ext import commands
import random
import time
import unicodedata
import asyncio
import uuid
import datetime
import heapq
import lavalink
import math
import re
import time
import io
import aiohttp
import json
import random

# Zowlcogs
from .qchecks import QChecks
from .bossfights import BossFights
from .questions import Questions

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


class Events:
    
    
        
    def __init__(self, bot):
        self.tasks = []
        self.bot = bot
        self.config = Config.get_conf(self, 8358350000, force_registration=True)
        

        event_defaults = {
            'Trivia': {
                'Questions': {
                    'Categories': {
                        'General':{
                                'Questions':{},
                                'Info': 'The most general category.'
                            },
                        'Rick and Morty':{
                                'Questions':{},
                                'Info': 'Wubba lubba quiz quiz? Something like that?'
                            }
                        }
                },
                'AQuestions': {
                    'Categories': {
                        'General':{
                                'Questions':{},
                                'Info': 'The most general category.'
                            }
                        }
                }
            }
        }
        
        self.config.register_guild(**event_defaults)


    @commands.group(autohelp=True)
    async def events(self, ctx):
        """Commands regarding the bot's server events!"""
        pass
    
    #@checks.is_owner()
    #@commands.command()
    async def fite(self, ctx, channel=None):
        data = await self.import_json()
        if channel is None:
            channel = ctx.channel

        bf = BossFights(ctx, self.bot, self.config, data, channel)
        await bf.start_fight()

    @checks.is_owner()       
    @commands.command()    
    async def f_l(self, ctx):
        """Loops bossfights in a specified category!"""
        self.tasks.append(self.bot.loop.create_task(self.f_loop(ctx)))


    async def f_loop(self, ctx):
        while self == self.bot.get_cog("Events"): 
            # Top one is R&M, the "General" category.
            channels = ctx.guild.get_channel(360568952125915136).channels 
            # channels = ctx.guild.get_channel(476732992925073428).channels

            #Picks a random chat channe not in the blocklist.
            ricksclusive = discord.utils.get(ctx.guild.channels,id=311605411016867840)
            askthemods = discord.utils.get(ctx.guild.channels,id=304062187482382356)
            blocklist = [ricksclusive, askthemods]
            while self == self.bot.get_cog("Events"):
                channel = random.choice(channels)
                if channel not in blocklist:
                    break

            # Allows Chip to talk in channel.
            await channel.set_permissions(self.bot.user, read_messages = True, send_messages = True)
            # Minutes before boss arrives.
            minutenumber = 2
            # FIX THIS
            role =  discord.utils.get(ctx.guild.roles,id=477656812997312514)
            await role.edit(mentionable=True)#
            delmsgbefore = await channel.send("<@&477656812997312514>")
            await role.edit(mentionable=False)
            
            delmeggies = []
            delmeggies.append(delmsgbefore)
            delemsg1 = await channel.send("A boss is arriving in {} minutes! Ready yourselves!".format(minutenumber))
            delmeggies.append(delemsg1)
            # FIX THIS
            for i in range(minutenumber):
                nr = i+1
                await asyncio.sleep(60)
                delmeggies.append(await channel.send("A boss is arriving in {} minutes! Ready yourselves!".format(minutenumber-nr)))
            
            for meggie in delmeggies:
                await meggie.delete()

            # Makes it so people can't write or react in the channel!
            #print("Pre-reactions")
            await channel.set_permissions(ctx.guild.default_role, read_messages=True, send_messages=False, add_reactions=False)
            await channel.set_permissions(self.bot.user, send_messages=True, add_reactions = True)
            #print("Post-reactions")

            

            #FIGHT
            await self.fite(ctx, channel)

            #Makes it so people CAN write in the channel.
            await channel.set_permissions(ctx.guild.default_role, read_messages=True, send_messages=True, add_reactions=True)
            #Makes it so Chip CAN write in the channel.
            await channel.set_permissions(self.bot.user, read_messages=False, send_messages=False)

            cooldown = random.randint(1800,5400)
            await asyncio.sleep(cooldown)

 

    async def import_json(self): 
        #path = bundled_data_path(self) / 'data.json'
        path = '/home/redbot/Documents/json.json'
        with open(path, encoding="utf8") as f:
            data = json.load(f)
        return data

    """@commands.command()
    async def asdasdasdasd(self, ctx):
        user = ctx.author.id
        self.gconf = self.config.guild(ctx.guild)
        bosskills = await self.gconf.set_raw(user, 'bossfights',value={})"""


    """weaponnamelist = list(weaponname)
        for index, name in enumerate(weaponnamelist):
            weaponnamelist[index] = name.title()

        weaponnamelist = """
    
    @commands.command()
    async def wemoji(self, ctx, *weaponname):
        """Displays which emoji one uses to equip a weapon."""
        data = await self.import_json()
        weaponname = " ".join(weaponname)
        try:
            emoji = data["items"][weaponname]["Emoji"]
            await ctx.send(emoji)
        except KeyError:
            await ctx.send("That's not a weapon.\n*Remember that `=wemoji` is case sensitive.*\n✔️ `=wemoji Saxophone`\n❌`=wemoji saxophone`")

    @commands.command()
    async def bosskills(self, ctx, user : discord.Member=None):
        self.gconf = self.config.guild(ctx.guild)
        if user is None:
            user = ctx.author
        try:
            bosskills = await self.gconf.get_raw('bossfights', 'users', user.id, 'kills')
        except KeyError:
            bosskills = 0

        return await ctx.send("This user has slain **{}** bosses!".format(bosskills))

    @commands.command()
    async def textpost(self, ctx):
        await ctx.send(".")

    @commands.command()
    async def temp_copy(self, ctx):
        self.instance = await self.get_instance(ctx, settings=True, user=ctx.author)
        self.gconf = self.config.guild(ctx.guild)
        questions = await self.gconf.get_raw('Questions')
        aquestions = await self.gconf.get_raw('AQuestions')
        await self.instance.set_raw('Trivia','AQuestions', value = aquestions)
        await self.instance.set_raw('Trivia','Questions', value = questions)

    """@commands.command()
    async def cdtest(self,ctx):
        await ctx.send("Hei")
        for i in range(3):
            await ctx.send("Skjei")
            await asyncio.sleep(1)
            await ctx.send("Nei")

    @commands.command()
    async def rmtest(self,ctx):
        thing = await ctx.bot.wait_for('message','reaction_add',timeout=10)
        await ctx.send(thing)

    


    @commands.command()
    async def itest(self, ctx):
        embed = discord.Embed()
        embed.set_image(url="https://vignette.wikia.nocookie.net/clubpenguin/images/b/b7/Club_Penguin_Island_Logo.png/revision/latest?cb=20161118003728")
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(2)
        embed.set_image(url="https://i.imgur.com/sqEqgZa.png")
        await msg.edit(embed=embed)

    @commands.command()
    async def edittest(self, ctx):
        delmsg = await ctx.send("Balls")
        await delmsg.edit(content=(
            "I'll host a new round of One Word Story in **{}** minutes."))

    @commands.command()
    async def pintest(self, ctx):
        delmsg = await ctx.send("Balls")
        await delmsg.pin()
    
    @commands.command()
    async def plpic(self, ctx):
        # Coins image
            async with aiohttp.ClientSession() as session:
                async with session.get('https://i.imgur.com/TfXisK4.png') as resp:
                    if resp.status != 200:
                        return await ctx.channel.send('Could not download file...')
                    data = io.BytesIO(await resp.read())
                    asdasdasd = await ctx.send(file=discord.File(data, 'TfXisK4.png'))        
"""
    @commands.command()
    async def tatest(self, ctx):
        tasks = [self.bot.wait_for(event) for event in ['reaction_add', 'message']]
        done, left = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        [task.cancel() for task in left]
        try:
            result = done.pop().result()
        except IndexError:
            pass
        else:
            if isinstance(result, tuple):
                reaction, user = result  # is a reaction_add or reaction_remove
                await ctx.send("REACTIONS")
            else:
                message = result  # is a message
                await ctx.send("MESSAGE")




    def __unload(self):
        for task in self.tasks:
            task.cancel()
     
    @checks.is_owner()       
    @commands.command()    
    async def q_l(self,ctx):
        """Loops trivia rounds in the current channel!"""
        self.tasks.append(self.bot.loop.create_task(self.q_loop(ctx)))

    async def q_loop(self,ctx):
        while self == self.bot.get_cog("Events"):
            countdown = 60
            # Makes the role pingable, then unpingable.
            role =  discord.utils.get(ctx.guild.roles,id=477832456033140736)
            await role.edit(mentionable=True)
            triviamsg = await ctx.send("<@&477832456033140736>\n❓ **TRIVIA ROUND!** ❓")
            startmsg = await ctx.send("Alright ye ding dongs, time to answer some questions for {}!\n" \
                                        "*We will be starting in* **{}** *seconds!*".format(await bank.get_currency_name(ctx.guild),countdown))

            await role.edit(mentionable=False)
            await asyncio.sleep(countdown)
            await startmsg.delete()

            counter = 0
            gamemoney = 0
            while counter < 5:
                await asyncio.sleep(3)
                alsodelmsg = await ctx.send("Alright, question!")
                await asyncio.sleep(2)
                turnmoney = await self.rtest(ctx)
                gamemoney += turnmoney
                counter += 1
                await alsodelmsg.delete()
            # Counts down the time until the next OWS.
            
            await triviamsg.delete()
            awardmsg = await ctx.send("{}{} were awarded this game!".format(gamemoney, await bank.get_currency_name(ctx.guild)))
            await asyncio.sleep(20)
            await awardmsg.delete()
            
            minutenumber=60
            delmsg = await ctx.send("I'll host another Trivia Round in **{}** minutes.".format(minutenumber))
            
            await delmsg.pin()

            # Deletes pin msg.
            async for message in ctx.history(limit=1):
                await message.delete()

            for i in range(minutenumber):
                i += 1
                await asyncio.sleep(60)
                await delmsg.edit(content=(
                    "I'll host another Trivia Round in **{}** minutes.".format(minutenumber-i)))

            await delmsg.delete()

    # Picks a random category based on amount of questions.
    async def randomcategory(self, categoriesdict):
        
        catlengths = {}
        total_length = 0
	
        for key, value in categoriesdict.items():
            for stringy, allqs in value.items():
                nr_questions = int(len(allqs))
                catlengths[key] = nr_questions
                total_length += nr_questions
                break


        """
        Picks a random number from 0 to the amount of questions in total.
        It starts checking the dict. If the lengthnr in the dict is larger than the rnr, then it returns that as a string.
        If not, it subtracts the lengthnr from rnr.
        The reason this is built this way is to ensure true randomness, even if categories have even lengths.
        """
        rnr = random.randint(0,total_length)

        for cat, number in catlengths.items():
            if number > rnr:
                category = cat
                break
            else:
                rnr -= number

        return category

        

    async def rtest(self,ctx):
        try:
        
            awardamount = 6
            
            category = 'General'
            self.gconf = self.config.guild(ctx.guild)
            async with self.gconf.Trivia.AQuestions() as aquestions:
                cats = aquestions['Categories']
                category = await self.randomcategory(cats)
                await ctx.send(category)

            # Gets a random question.
            question, questiondict = await self.randomquestion(ctx, category)
            answer_index = questiondict.get("Correct_alt_index")
            alternatives = questiondict.get("Alternatives")
            emojis = ["\u0031\u20E3","\u0032\u20E3","\u0033\u20E3","\u0034\u20E3"]
            emoji_answer_index = answer_index
            correct_react = None
            
            # Gets questions cooldown.
            cooldowns = ctx.bot.get_cog('Cooldowns')
            cooldown = await cooldowns.get_default_cooldown(ctx, 'Events', 'Questions')
            
            #Function for editings
            def embed_edit(message, number):
                embed = next(iter(message.embeds))
                embed.title = ('{}  ({})').format(question, cooldown)
                return embed
                
           # Creates embed based on question
            embed_desc = ""
            for i, alternative in enumerate(alternatives):
                embed_desc = "{}{}. {}\n".format(embed_desc, i+1, alternative)
                if emoji_answer_index == i:
                    correct_react = emojis[i]
                    
            embed = discord.Embed(
                colour=ctx.guild.me.top_role.colour,
                title = ('{}  ({})').format(question, cooldown),
                description = embed_desc
                )

            # Creates an embed with the highlighted correct answer.
            correct_embed_desc = ""
            for i, alternative in enumerate(alternatives):
                if emoji_answer_index == i:
                    alternative = " **" + alternative + "**"
                correct_embed_desc = "{}{}. {}\n".format(correct_embed_desc, i+1, alternative)

            correct_embed = discord.Embed(
                colour=ctx.guild.me.top_role.colour,
                title = question,
                description = correct_embed_desc
                )
            
            # Sends the created embed and adds reactions
            message = await ctx.send(embed=embed)
            for i in emojis:
                await message.add_reaction(i)
            
            doneit = False
            
            # Goes for as many repetitions as there are seconds in the cooldown.
            while(not doneit):      
                await asyncio.sleep(1)
                cooldown = cooldown - 1
                embed =  embed_edit(message, cooldown)
                await message.edit(embed=embed)
                if cooldown == 0:
                    doneit = True

            # Prints a new embed where the correct alternative is highlighted.
            await message.edit(embed=correct_embed)

            # Makes a list consisting of Member objects out of all the users who reacted correctly and also wrongly.
            # Does what I want now.
            reactionlist = []
            wrongreactionlist = []
            message = await message.channel.get_message(message.id)
            number = 0
            
            for x in message.reactions:
                newthing = discord.utils.get(message.reactions, emoji=emojis[number])
                newthing = await newthing.users().flatten()
                
                if number == emoji_answer_index:
                    reactionlist.append(newthing)
                else:
                    wrongreactionlist.append(newthing)
                    
                number += 1
            
            # Makes a unique list with all reactors' IDs.
            correctusers = []
            for i in reactionlist:
                for x in i:
                    if x not in correctusers:
                        correctusers.append(x)
           
            incorrectusers = []
            for i in wrongreactionlist:
                for x in i:
                    if x not in incorrectusers:
                        incorrectusers.append(x)
          
           
            # Removes double-voters
            forcorrectusers = correctusers  
            for x in incorrectusers:
                if x in forcorrectusers:
                    correctusers.remove(x)
          
            # Adds money to the users
            for i in correctusers:
                await bank.deposit_credits(i, awardamount)
            
            # Prints the correct alternative!
            correctcounter = len(correctusers)
            wrongcounter = len(incorrectusers)-1
            turnmoney = correctcounter*awardamount
            self.gconf = self.config.guild(ctx.guild)
            
            sendtext = "{} users responded correctly and were rewarded {} {}! \n"
            if wrongcounter == 0:
                fail_lines = ["And surprisingly, {} users responded incorrectly. Y'all dingdongs Google fast.","And {} users responded incorrectly. Huh.",
                                "And {} people responded incorrectly? d fck"]
                fail_text = random.choice(fail_lines)
                sendtext += fail_text
            else:
                fail_lines = ["{} users responded incorrectly lmao.", "{} people responded incorrectly hahah how tho",
                    "And {} users responded the **incorrect** answer which is **not** the point here.", 
                    "And {} just clicked something.",
                    "And {} users decided that they didn't want any money at all. *shrug*",
                    "Really? {} people got that wrong. Y'all are dumber than I thought.",
                    "{} people are dumber than a 5th grader.",
                    "To say I am dissapointed would be an understatement. __**{}**__ people clearly have no idea what they are doing...",
                    "Aaannd {} people fucked up. *Nice* *Reeeeeeal nice.*",
                    "Aw, {} people got that one wrong. Maybe you'll do better next time. *maybe*"]
                fail_text = random.choice(fail_lines)
                sendtext += fail_text
                
            newmessage = await ctx.send(sendtext.format(correctcounter,awardamount,await bank.get_currency_name(ctx.guild),wrongcounter))
            
            await self._clear_react(message)
            
            await asyncio.sleep(10)
            await message.delete()
            await newmessage.delete()
            return turnmoney

        except IndexError:
            return await ctx.send("There are no questions to choose from!")
         
    @events.command()
    async def question(self, ctx, action: str):
        """Commands relevant for questions!"""
        
        """Configures the event questions.
        **create** Creates a new question with alternatives 
        **del** Deletes a question,.
        **list** Lists all approved or pending questions.
        **append** Pushes a question from pending to approved.
        **append_all** Pushes all questions in a category to approved."""
        
        instance = await self.get_instance(ctx, settings=True, user=ctx.author)
        
        if action.lower() not in ('create', 'del', 'list', 'append','append_all'):
            return await ctx.send("Must pick create, del, list, append or append_all.")
        #elif action.lower in ('append','append_all'):
         #   if self.gconfig.role()
        
        q = Questions(ctx, instance, self.bot)
                
        try:
            await q.run(action)
        except asyncio.TimeoutError:
            return await ctx.send("Request timed out. Process canceled.")
    
    async def randomquestion(self, ctx, category):
            
            self.instance = await self.get_instance(ctx, settings=True, user=ctx.author)
            async with self.gconf.Trivia.AQuestions() as aquestions:
            
                """categorydict = await self.gconf.get_raw('AQuestions','Categories',category)
                
                question = random.choice(list(categorydict.keys()))
              
                questiondict = await self.gconf.get_raw('AQuestions','Categories',category,'Questions',question)"""
                
                categorydict = aquestions['Categories'][category]
                questionsdict = categorydict['Questions']
                
                question = random.choice(list(questionsdict.keys()))
              
                """print(aquestions['Categories'][category])
                questiondict = await self.instance.get_raw('AQuestions','Categories',category,'Questions',question)"""
                questiondict = questionsdict[question]
              
                return question, questiondict
    
    #@checks.mod_or_permissions(administrator=True)
    # @checks.mod_or_permissions(administrator=True)
    
            
        
            
    @staticmethod
    async def _clear_react(message):
        try:
            await message.clear_reactions()
        except (discord.Forbidden, discord.HTTPException):
            return       
            
            
    async def get_instance(self, ctx, settings=True, user=None):
        if not user:
            user = ctx.author
        return self.config.guild(ctx.guild)
        """if await self.config.Global():
            if settings:f
                return self.config
            else:
                return self.config.user(user)
        else:
        if settings:
            return self.config.guild(ctx.guild)
        else:
            return self.config.member(user)"""
       
       
    @commands.command()
    async def worth(self, ctx):
        """Display the worth of a Schmekle!"""
        currency = await bank.get_currency_name(ctx.guild)
        await ctx.send("According to a waitress in 'Thirsty Step', one boob job costs 25 {}.\
                    A regular boob job in the US costs $3,708, meaning that 1 {} = $148.32. Y'all loaded.".format(currency, currency))
                
                

                
    """
    gets boss fight data from specific guild without the need for ctx

    Parameters
    ----------
        guild: int
            id of guild to get instance from


    """
    async def get_boss_kills(self, guild):

        return await self.config.guild(self.bot.get_guild(guild)).get_raw('bossfights', 'users')


    """
    send images for #leaderboard
    """
    @checks.is_owner()
    @commands.command()
    async def bfpicpost(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://i.imgur.com/qZjGA7z.png') as resp:
                if resp.status != 200:
                    return await ctx.channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                imgtitle = await ctx.send(file=discord.File(data, 'qZjGA7z.png'))

    @checks.is_owner()
    @commands.command()
    async def blcpicpost(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://i.imgur.com/nHCPozo.png') as resp:
                if resp.status != 200:
                    return await ctx.channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                imgtitle = await ctx.send(file=discord.File(data, 'nHCPozo.png'))
    
    @commands.command()
    async def bf_copy(self, ctx):
        # Increases users boss participation.
        self.gconf = self.config.guild(ctx.guild)
        participating_users = [233669548673335296, 118446786988867587]
        for userid in participating_users:
            bosscounter = await self.gconf.get_raw('users', userid, 'bossfights', 'Kills')
            await self.gconf.set_raw('bossfights', 'users', userid, 'kills', value=bosscounter)