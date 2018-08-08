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
        self.bot = bot
        self.config = Config.get_conf(self, 8358350000, force_registration=True)
        

        event_defaults = {
            'Questions': {
                'Categories': {
                    'General':{
                            'Questions':{},
                            'Info': 'The most general category.'
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
    
    @commands.command()
    async def fite(self,ctx):
        
        bf = BossFights(ctx, self.bot, self.config)
        await bf.start_fight()
    
    
    @checks.is_owner()
    @commands.command()
    async def rtest(self,ctx):
        try:
        
            awardamount = 10
            
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
            self.gconf = self.config.guild(ctx.guild)
            
            sendtext = "{} users responded correctly and were rewarded {} {}! \n"
            if wrongcounter == 0:
                sendtext += "And surprisingly, {} users responded incorrectly. Y'all dingdongs Google fast."
            else:
                sendtext += "{} users responded incorrectly lmao git good you fuckheads."
                
            await ctx.send(sendtext.format(correctcounter,awardamount,await bank.get_currency_name(ctx.guild),wrongcounter))
            
            await self._clear_react(message)
            
            await asyncio.sleep(5)
            await message.delete()
            
        except IndexError:
            return await ctx.send("There are no questions to choose from!")
         
    @events.command()
    async def question(self, ctx, action: str):
        """Commands relevant for questions!"""
        
        instance = await self.get_instance(ctx, settings=True, user=ctx.author)
        
        if action.lower() not in ('create', 'del', 'list', 'append','append_all'):
            return await ctx.send("Must pick create, del, list, append or append_all.")
        #elif action.lower in ('append','append_all'):
         #   if self.gconfig.role()
        
        q = Questions(ctx, instance)
                
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
            await ctx.send("Exception town")
            return       
            
            
    async def get_instance(self, ctx, settings=True, user=None):
        if not user:
            user = ctx.author
        return self.config.guild(ctx.guild)
        """if await self.config.Global():
            if settings:
                return self.config
            else:
                return self.config.user(user)
        else:
        if settings:
            return self.config.guild(ctx.guild)
        else:
            return self.config.member(user)"""
       
       
                
                
                

    
    