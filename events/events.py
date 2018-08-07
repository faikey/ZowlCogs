import discord
from discord.ext import commands
import random
import time
import unicodedata
import asyncio
from .qchecks import QChecks
import logging
import uuid
import aiohttp
import asyncio
import datetime
import discord
import heapq
import lavalink
import math
import re
import time
import redbot.core

# Red
from redbot.core import Config, bank, commands
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


# Discord.py
import discord

# Red
from redbot.core import Config, bank, commands
from redbot.core.data_manager import bundled_data_path

class Events:
    
    #ADD MANUAL ID
    
    
    # Shit won't work, idk why. See https://github.com/Redjumpman/Jumper-Plugins/blob/V3/shop/shop.py#L751 for what has
    # been attempted implemented. Error comes from check_set_q_id, cause there's no categrory. 
    
    # How to fix couroutine object error again...
        
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
        self.config.register_member(**event_defaults)
        self.config.register_user(**event_defaults)
        
        print("Guild Print: ")
        print(self.config.register_guild(**event_defaults))

    # Make it so it stores users reacting before running new code.
    """},
            'AQuestions': {
                'Categories': {}
                }"""

    
    @commands.group(autohelp=True)
    async def events(self, ctx):
        """Commands regarding the bot's server events!"""
        pass
        
    @commands.command()
    async def gettest(self, ctx):
    
        self.gconf = self.config.guild(ctx.guild)
        
        print("HEI JARLEE")
        await self.gconf.set_raw('test', value={'othertest':{}} )
        await self.gconf.set_raw('test','othertest', value="testval")
        dicty = await self.gconf.get_raw('test','othertest')
        printy = await self.gconf.get_raw('Questions')
        print(dicty)
        #await ctx.send(dict)   
        #await ctx.send(printy)          

    @events.command()
    async def question(self, ctx, action: str):
        """Commands relevant for questions!"""
        
        instance = await self.get_instance(ctx, settings=True, user=ctx.author)
        
        if action.lower() not in ('create', 'del', 'list', 'append','append_all'):
            return await ctx.send("Must pick create, del, list, append or append_all.")
        
        qm = QuestionManager(ctx, instance)
                
        try:
            await qm.run(action)
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
    
    @commands.command()
    async def startevent(self, ctx):
        # Define what channel.
        
        #SOME WORK
        category = 'General'
        self.gconf = self.config.guild(ctx.guild)
        # await self.initrun(ctx)
        
        
        question, questiondict = await self.randomquestion(ctx, category)

        answer_index = questiondict.get("Correct_alt_index")
        
        alternatives = questiondict.get("Alternatives")
        
        emojis = ["\u0031\u20E3","\u0032\u20E3","\u0033\u20E3","\u0034\u20E3"]

        emoji_answer_index = answer_index

        correct_react = None
            
        embed_desc = ""
        for i, alternative in enumerate(alternatives):
            embed_desc = "{}{}. {}\n".format(embed_desc, i+1, alternative)
            if emoji_answer_index == i:
                correct_react = emojis[i]
                
        
        embed = discord.Embed(
            colour=ctx.guild.me.top_role.colour,
            title = question,
            description = embed_desc
            )
            
             
        message = await ctx.send(embed=embed)
        
        for i in emojis:
            await message.add_reaction(i)
            
        def check(reaction, user):
            return (
                reaction.message.id == message.id 
                and user == ctx.message.author
                # and any(e in str(r.emoji) for e in expected)
            )

            
        try:
            (r, u) = await self.bot.wait_for("reaction_add", timeout=12.0, check=check)
        except asyncio.TimeoutError:
            return await self._clear_react(message)
            
        # r_unicode = unicodedata.name(r)
        #client = discord.Client()
        r = r.emoji
        await ctx.send("{} ANDNDNN {}".format(r, correct_react))
        print("{} ANDNDNN {}".format(r, correct_react))
        
        if r == correct_react:
            await ctx.send("Congrats homie, correctly reacted!")
            await self._clear_react(message)
        else:
            await ctx.send("Stop answering incorrectly you fucking dope")
            
            
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
       
       
                
                
                
class QuestionManager:

    def __init__(self, ctx, instance):
        self.instance = instance
        self.ctx = ctx
        
        
    async def run(self, action):

        if action.lower() == "create":
            await self.create()
        elif action.lower() == "del":
            await self.delete()
        elif action.lower() == "append":
            await self.append()
        elif action.lower() == "append_all":
            await self.append_all()
        elif action.lower() == "list":
            await self.list()
        else:
            print("No correct commands")
            
      
    async def append(self):
        try:
            async with self.instance.Questions() as questions:
                (categorynr, categoryarray) = await self.pick('Categories','pickcategory', questions)
            
                dicty = categoryarray[categorynr]
                
                print(dicty)
                await self.ctx.send("What question ID?")
                id = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).same)
                print("QE")
                id = id.content
                
                print(id)
                
                questiondict = questions['Categories'][category]['Questions']
                question = ''
                
                for forquestion, value in questiondict.items():
                    if 'id' in value:
                        if value['id'] == id:
                            question = forquestion
                
                questiondata =  await self.instance.get_raw('Questions','Categories', category, 'Questions', question)
                await self.instance.set_raw('AQuestions','Categories', category, 'Questions', question, value = questiondata)
                del questions['Categories'][category]['Questions'][question]
                await self.ctx.send('Question approved!')
                
        except KeyError:
            return await self.ctx.send("That category does not exist!")
                
            
                
    
    async def append_all(self):
        try:
            async with self.instance.Questions() as questions:
                
                (categorynr, categoryarray) = await self.pick('Categories', 'list', questions)
        
                dicty = categoryarray[categorynr]
               
                for question in dicty.keys():
                    async with self.instance.Questions() as questions:
                        questiondata =  await self.instance.get_raw('Questions','Categories', category, 'Questions', question)
                        await self.instance.set_raw('AQuestions','Categories', category, 'Questions', question, value = questiondata)
                        del questions['Categories'][category]['Questions'][question]
                        await self.ctx.send('Question approved!')
                        
        except KeyError:
            return await self.ctx.send("That category does not exist!")
                
          
    async def list(self):
   
        questions, which = await self.get_dict()        
        if not questions:
                return
        
        (categorynr, categoryarray) = await self.pick('Categories','pickcategory', questions)
        
        d = categoryarray[categorynr]
      
        if not d:
            return await self.ctx.send("This category is empty!")
            
        (questionnr, questionarray) = await self.pick(d,'listquestions', questions, which)
        return

      
    async def delete(self):
        
        try:
            
            questions, which = await self.get_dict()
            
            if not questions:
                return
            
            (categorynr, categoryarray) = await self.pick('Categories','pickcategory', questions)
            
            categorydel = categoryarray[categorynr]
            
            (questionnr, questionarray) = await self.pick(categorydel, 'pickquestion', questions)
            # questions['Categories'][categorydel][
            questiondel = questionarray[questionnr]
            
            if which == 'pending':
                async with self.instance.Questions() as questions:
                 del questions['Categories'][categorydel]['Questions'][questiondel]
            else:
                async with self.instance.AQuestions() as questions:
                    del questions['Categories'][categorydel]['Questions'][questiondel]
        
            await self.ctx.send("Question deleted!")
            #await self.id_check('question', categorydel)
      
    
        except KeyError:
            await self.ctx.send("Keyrror?")
            return
            
            
    async def get_dict(self):
        
        await self.ctx.send("Pending or approved?")
            
        which = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).same)
        which = which.content
        which = which.lower()
            
        if which not in ('pending', 'approved'):
            return await self.ctx.send("Must be pending or list. Process terminated.")
            
        questions = await self.questionsdict(which)
        return questions, which
            

    async def questionsdict(self, q):
       
        if q == 'pending':
            async with self.instance.Questions() as questions:
                return questions
        else:
            async with self.instance.AQuestions() as questions:
                return questions
            
        return returndict 
   
    async def pick(self, value, function, dicty, which=None):
            questions = dicty
            nr = 0
            temp_array = []
        
            """dbtest = await self.valuetest(value, function)
            if(not dbtest):
               return False"""
           
            if function == 'pickcategory':
                await self.ctx.send("Which category number?")
                dicty = questions['Categories']
            elif function == 'listcategories':
                dicty = questions['Categories']
            elif function == 'listquestions':
                dicty = questions['Categories'][value]['Questions']
            else:  
                await self.ctx.send("Which question number?")
                dicty = questions['Categories'][value]['Questions']

            
            embed_desc = ''
            embed_title = ''
            
            if which == 'approved':
                embed_title = 'Approved Questions'
            elif which == 'pending':
                embed_title = 'Pending Questions'
            else:
                embed_title = 'Questions'
            
            for key, value in dicty.items():
                nr = nr + 1 
                temp_array.append(key)
                if function == 'pickcategory' or function == 'listcategories':
                    embed_desc += ("{}. {} \n".format(nr, key))
                    embed_title = 'Categories'
                else:
                    embed_desc += ("{}. {} - {}\n".format(nr, key, value['id']))
                    
            
                    
            
            embed = discord.Embed(
                colour=self.ctx.guild.me.top_role.colour,
                title = embed_title,
                description = embed_desc
            )
             
            await self.ctx.send(embed=embed)
            
            if value == 'listquestions':
                answernr = 0
            else:
                answer = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).positive)
                answernr = int(answer.content)-1 
                
            return answernr, temp_array
    
    
    
    async def valuetest(self, value, function):
        async with self.instance.Question() as questions:
            print(" valuetest --->" + value + "<----")
            try: 
                testint = 0
                if value == 'Categories':
                    d = questions['Categories']
                else:
                    d = questions['Categories'][value]
                for i in d:
                    testint += 1
                
                if testint == 0:
                    raise TypeError
                
                return True
          
            except TypeError:
                    if function == 'del':
                        del questions['Categories'][value]
                        await self.ctx.send("Category deleted!")
                        #await self.id_check('category')
                        return False
                    else:
                        await self.ctx.send("There are no categories?")
                        return False

            except NameError:
                await self.ctx.send("There are no categories!")
                return False

    """#why do I have IDs again
    sync def id_check(self, whatremoved, category=None):
        
        if whatremoved is 'categiry':
            categories = self.instance.Questions()['Categories']
            d = categorieas
            counter = 1
            for i in d:
                if i['id'] is not counter:
                    self.instance.Questions()['Categories'][i]['id': counter]
                    
                    
        else:
            questions = self.instance.Questions()['Categories'][category]['Questions']
            d = questions
            counter = 1
            for i in d:
                if i['id'] is not counter:
                    self.instance.Questions()['Categories'][i]['id': counter]"""
                     
       
        
            
                
    async def create(self):
    
        question = await self.set_question()
        
        alternatives = []
        
        for i in range(4):
            alternatives.append(await self.set_alternative(i))
            
        correct_alt_index = await self.set_correct_alt()
        
        id = await self.set_q_id()
        
        print("Create id:")
        print (id)
        
        data = {'id' : id, 
                'Alternatives': alternatives,
                'Correct_alt_index': correct_alt_index
                }
        
        await self.add(data, question)
        await self.ctx.send("Question added!")
        
    async def add(self, data, question):
    
        #async with self.instance.Questions() as questions:
        
        print(question)
        questions = await self.instance.Questions.all()
            
        category = 'General'

        print("Questons print:")
        print(questions)
      
        if category not in questions['Categories']:
            questions['Categories'][category]['Questions'] = {question: data}
        
        elif question in questions['Categories'][category]['Questions']:
             await self.ctx.send("Question already exists!")
            
        else:
            #questions['Categories'][category]['Questions'][question] = data
            await self.instance.set_raw('Questions','Categories', category, 'Questions', question, value = data)
            print(await self.instance.get_raw('Questions', 'Categories', category, 'Questions',question))
            print(await self.instance.get_raw('Questions','Categories', category, 'Questions',question))
            
        print("END PRINT  ")
        print(questions)
        print("ALL QUESTIONS THING")
        print(await self.instance.Questions.all())
        
       
      
            #return await self.instance.set_raw('Questions','Categories', category, new_id, value = data)
            
            
    # def pending_add(self, data):
     #   await self.list()
        
    # not functional
    
    async def set_q_id(self):
          
            return str(uuid.uuid4())


  
    async def set_question(self):

        
        await self.ctx.send("Enter the question:")
        
        question = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).same)
        
        return question.content
    
    
    async def set_alternative(self, number):
        await self.ctx.send("Set alternative {}:".format(number+1))
        
        alternative = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).same)
        
        content = alternative.content
        
        if content is None:
            content = 'blank'
        
        return content
        
    async def set_correct_alt(self):
        await self.ctx.send("Which alternative is the correct one? (1-4)")

        correct_alt = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).alt_nr)
        return int(correct_alt.content) - 1
    
    
    