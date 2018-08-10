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

# Discord.py
import discord


class Questions:

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
                
                if not isinstance(categorynr, int):
                    return
                
                category = categoryarray[categorynr]
                
                d = categoryarray[categorynr]
                        
                (questionnr, questionarray) = await self.pick(d, 'pickquestion', questions, 'pending')
                
                if not isinstance(questionnr, int):
                    return
                
                question = questionarray[questionnr]
                
                while(True):
                    questiondata =  await self.instance.get_raw('Questions','Categories', category, 'Questions', question)
                    await self.instance.set_raw('AQuestions','Categories', category, 'Questions', question, value = questiondata)
                    del questions['Categories'][category]['Questions'][question]
                    await self.ctx.send('Question approved! Continue?')
                    answer = await self.ctx.bot.wait_for("message", timeout=10.0, check=QChecks(self.ctx).same)
                    answer = answer.content.lower()
                   
                    if answer in ('yes','y'):
                        (questionnr, questionarray) = await self.pick(d, 'pickquestion', questions, 'pending')
                        question = questionarray[questionnr]
                    else:
                        await self.ctx.send('Cancelling process!')
                        return
                
        except KeyError:
            return await self.ctx.send("That category/id does not exist!")
        except IndexError:
            return await self.ctx.send("This category is empty!")
        except TypeError:
            return
            
                
    
    async def append_all(self):
        #try:
            async with self.instance.Questions() as questions:
                
                (categorynr, categoryarray) = await self.pick('Categories', 'pickcategory', questions)
                
                print("HERE COMES THE PRINTS")
                print(categoryarray)
                print(categorynr)
                
                category = categoryarray[categorynr]
                categorydict = questions['Categories'][category]
                print(categorydict)
               
                for x, i in categorydict.items():
                    for question in i.keys():
                        async with self.instance.Questions() as questions:
                            print(question)
                            questiondata =  await self.instance.get_raw('Questions','Categories', category, 'Questions', question)
                            await self.instance.set_raw('AQuestions','Categories', category, 'Questions', question, value = questiondata)
                            del questions['Categories'][category]['Questions'][question]
                            await self.ctx.send('Question approved!')
                        
                await self.ctx.send('All questions approved!')
        #except KeyError:
            #return await self.ctx.send("That category/id does not exist!")
                
          
    async def list(self):
        try:
            questions, which = await self.get_dict()        
            
            
            (categorynr, categoryarray) = await self.pick('Categories','pickcategory', questions)
            
            d = categoryarray[categorynr]
          
            if not d:
                return await self.ctx.send("This category is empty!")
                
            (questionnr, questionarray) = await self.pick(d, 'pickquestion', questions, which)
            
            q = questionarray[questionnr]
            
            if not q:
                return await self.ctx.send("This category is empty!")
            
            
            while(True):
                (questionnr, questionarray) = await self.pick(d, 'listalternatives', questions, which, q)
                await self.ctx.send("Continue?")
                
                answer = await self.ctx.bot.wait_for("message", timeout=7.0, check=QChecks(self.ctx).same)
                answer = answer.content
                       
                if answer in ('yes','y'):
                    (questionnr, questionarray) = await self.pick(d, 'pickquestion', questions, 'pending')
                    question = questionarray[questionnr]
                else:
                    await self.ctx.send('Cancelling process!')
                    return
    
            
        
        except IndexError:
            return await self.ctx.send("This category is empty!")
        except TypeError:
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
            while(True):
                if which == 'pending':
                    async with self.instance.Questions() as questions:
                     del questions['Categories'][categorydel]['Questions'][questiondel]
                else:
                    async with self.instance.AQuestions() as questions:
                        del questions['Categories'][categorydel]['Questions'][questiondel]
                
                
                await self.ctx.send("Question deleted! Continue?")
                answer = await self.ctx.bot.wait_for("message", timeout=10.0, check=QChecks(self.ctx).same)
                answer = answer.content.lower()
               
                if answer in ('yes','y'):
                    (questionnr, questionarray) = await self.pick(categorydel, 'pickquestion', questions, 'approved')
                    question = questionarray[questionnr]
                else:
                    await self.ctx.send('Cancelling process!')
                    return
      
    
        except KeyError:
            await self.ctx.send("Keyrror?")
            return
        except TypeError:
            return
            
    async def get_dict(self):
        
        await self.ctx.send("Pending or approved?")
            
        which = await self.ctx.bot.wait_for('message', timeout=12, check=QChecks(self.ctx).same)
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
            
        #return returndict 
   
    async def pick(self, value, function, dicty, which=None, question=None):
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
            elif function == 'pickquestion':
                await self.ctx.send("Which question number?")
                dicty = questions['Categories'][value]['Questions']
            elif function == 'listalternatives':
                dicty = questions['Categories'][value]['Questions'][question]['Alternatives']
                correct_alt_index = questions['Categories'][value]['Questions'][question]['Correct_alt_index']
                
            
            embed_desc = ''
            embed_title = ''
            
            if which == 'approved':
                embed_title = 'Approved Questions'
            elif which == 'pending':
                embed_title = 'Pending Questions'
            else:
                embed_title = 'Questions'
            
            if function == 'listalternatives':
                for alternative in dicty:
                    if correct_alt_index == nr:
                        alternative = "**" + alternative + "**"
                    nr = nr + 1 
                    temp_array.append(alternative)
                    embed_desc += ("{}. {} \n".format(nr, alternative))
                    embed_title = "Alternatives"
            
            else:
                for key, value in dicty.items():
                    nr = nr + 1 
                    temp_array.append(key)
                    if function == 'pickcategory' or function == 'listcategories':   
                        embed_desc += ("{}. {} \n".format(nr, key))
                        embed_title = 'Categories'
                    else:
                        embed_desc += ("{}. {} \n".format(nr, key))
                        
                        
            
                    
            
            embed = discord.Embed(
                colour=self.ctx.guild.me.top_role.colour,
                title = embed_title,
                description = embed_desc
            )
             
            await self.ctx.send(embed=embed)
            
            print(temp_array)
            
            if nr == 0:
                await self.ctx.send("There is nothing here.")
                return 'test', None
            elif function == 'listalternatives':
                return 'test', None
                return
                
            else:
                if value not in ('listcategories','listquestions'):
                    answer = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).positive)
                    answernr = int(answer.content)-1 
                else:
                    answernr = 0
                    
            return answernr, temp_array
             
    async def create(self):

        # Implement category creation!
        #category = await self.pick()
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