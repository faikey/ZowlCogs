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
        self.tasks.append(self.bot.loop.create_task(self.f_loop(ctx)))

    async def f_loop(self, ctx):
        while self == self.bot.get_cog("Events"): 
            # Top one is R&M.
            channels = ctx.guild.get_channel(474437663831621663).channels 
            #channels = ctx.guild.get_channel(476732992925073428).channels
            channel = random.choice(channels)
            await self.fite(ctx, channel)
            cooldown = random.randint(3600,10800)
            await asyncio.sleep(cooldown)

    async def import_json(self): 
        path = bundled_data_path(self) / 'data.json'
        print(path)
        with open(path, encoding="utf8") as f:
            data = json.load(f)

        return data

    @commands.command()
    async def weaponemoji(self, ctx, *weaponname):
        data = await self.import_json()
        weaponname = " ".join(weaponname)
        try:
            emoji = data["weapon_emoji"][weaponname]
            await ctx.send(emoji)
        except KeyError:
            await ctx.send("That's not a weapon.")

    @checks.is_owner()
    @commands.command()
    async def picpost(self, ctx):
        # Posts the "Boss Fight" title, an image of the boss as well as a message.
        async with aiohttp.ClientSession() as session:
            async with session.get('https://i.imgur.com/TfXisK4.png') as resp:
                if resp.status != 200:
                    return await ctx.channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                imgtitle = await ctx.send(file=discord.File(data, 'TfXisK4.png'))

    @commands.command()
    async def textpost(self, ctx):
        await ctx.send(".")

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
        print("We got here?")
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
        self.tasks.append(self.bot.loop.create_task(self.q_loop(ctx)))

    async def q_loop(self,ctx):
        while True:
            countdown = 60
            # Makes the role pingable, then unpingable.
            role =  discord.utils.get(ctx.guild.roles,id=477832456033140736)
            await role.edit(mentionable=True)
            startmsg = await ctx.send("<@&477832456033140736>\n❓ **TRIVIA ROUND!** ❓\nAlright ye ding dongs, time to answer some questions for {}!\n" \
                                        "*We will be starting in* **{}** *seconds!*".format(await bank.get_currency_name(ctx.guild),countdown))

            await role.edit(mentionable=False)
            await asyncio.sleep(countdown)

            counter = 0
            gamemoney = 0
            while counter < 5:
                turnmoney = await self.rtest(ctx)
                gamemoney += turnmoney
                counter += 1
                
                print("We got here also")
                await asyncio.sleep(3)
                alsodelmsg = await ctx.send("Alright, next question!")
                await asyncio.sleep(5)
                await alsodelmsg.delete()
            # Counts down the time until the next OWS.
            await startmsg.delete()
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
                print(i)
                i += 1
                await asyncio.sleep(60)
                await delmsg.edit(content=(
                    "I'll host another Trivia Round in **{}** minutes.".format(minutenumber-i)))

            await delmsg.delete()


    async def rtest(self,ctx):
        try:
        
            awardamount = 5
            
            category = 'General'
            self.gconf = self.config.guild(ctx.guild)
            
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
                print("Members from first?")
                print(newthing)
                
                if number == emoji_answer_index:
                    reactionlist.append(newthing)
                    print(number)
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
                fail_lines = ["And surprisingly, {} users responded incorrectly. Y'all dingdongs Google fast.","And {} users responded incorrectly. Huh."]
                fail_text = random.choice(fail_lines)
                sendtext += fail_text
            else:
                sendtext += "{} users responded incorrectly lmao git good you dimwits."
                
            newmessage = await ctx.send(sendtext.format(correctcounter,awardamount,await bank.get_currency_name(ctx.guild),wrongcounter))
            
            await self._clear_react(message)
            
            await asyncio.sleep(10)
            await message.delete()
            await newmessage.delete()
            print("We got here tho")
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
            async with self.gconf.AQuestions() as aquestions:
            
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
            print("Exception town")
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
       
       
                
                
                

    
    