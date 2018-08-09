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


# Red
from redbot.core import Config, bank, commands, checks

# Discord 
import discord
from discord.ext import commands

# Others
import asyncio
import datetime
import random


class OneWordStory:


    def __init__(self,bot):
        self.tasks = []
        self.bot = bot
        self.config = Config.get_conf(self, 8358350000, force_registration=True)
        
     
     
        ows_defaults = {'Cooldown': 2700,
                            'Counter': 0,
                            'Round_time': 5,
                            'Start_time': 5,
                            'Answer_time': 14,
                            'Max_words': 40
                            }
                            
        self.config.register_guild(**ows_defaults)
        

    def __unload(self):
        for task in self.tasks:
            task.cancel()
     
    @checks.is_owner()       
    @commands.command()    
    async def ows_l(self,ctx):
        self.tasks.append(self.bot.loop.create_task(self.ows_loop(ctx)))
        #await self.ows_loop(ctx)
    
    async def ows_loop(self, ctx):
        #while self.bot.get_cog('OneWordStory') is self:
        while True:
            
            cooldownadd = await self.ows_function(ctx)
            print("WE OUT HERE")
            cooldowns = ctx.bot.get_cog('Cooldowns')
            cooldown = await cooldowns.get_default_cooldown(ctx, 'One_Word_Story')
            #newcooldown = cooldownadd +  basecooldown
            #newnewcooldown = random.randint(newcooldown,newcooldown*2)
            print(cooldown)
            await asyncio.sleep(cooldown)
        await ctx.send("We didn't loop?")
        
   
    @commands.command()
    async def iter(self,ctx):
        lastmessageiter = discord.abc.Messageable.history(ctx.channel, limit=3)
        await iterfunc()
        
        async def iterfunc():
            async for message in lastmessageiter:
                await message.delete()
                
   
 
    async def ows_function(self, ctx):
    
        startup_lines = ["Did you hear of the...", "There once was a...", '"Morty, we gotta...',
                        "The old man from...","Somebody once told me...", "The universe is...",
                        "The fact of the matter is...", "Did you know that...", "Fyre makes soap out of...",
                        "The FBI doesnt know yet but...", "After a long talk my roommates and I decided that...",
                        "My father used to always say...", "This is America..."]
        
        try:
            counter = await self.config.guild(ctx.guild).get_raw('Counter')
        except KeyError:
            counter = await self.config.guild(ctx.guild).set_raw('Counter', value = 1)

        def usercheck(message):
            return message.author != self.bot.user
        
        join_users = list()
        begin = datetime.datetime.now()
        current = begin
        start_time = await self.config.guild(ctx.guild).get_raw('Start_time')
        
        await ctx.send("<@&476900791475634187>\n**ONE WORD STORY TIME!**\nBeep boop, Chip here! It's time to play 'One Word Story!' Type **ows** in the chat to join! We start in {} seconds!".format(start_time))
        
        # Adds users who type "ows" into a list.
        try:
            while True:
                current = datetime.datetime.now()
                message = await self.bot.wait_for('message',
                                              timeout=(start_time - (current-begin).seconds),check=usercheck
                                              )
                if message.author not in join_users and message.content.lower() == 'ows' and message.author != self.bot.user:
                    join_users.append(message.author)
                    await ctx.send("{} joined!".format(message.author.mention))
                
                message.delete()
                
        except asyncio.TimeoutError:
            pass
        
        if not join_users:
            delmsg = await ctx.send("Oh. Well, I uh, I had better things to do anyways than play games! Like uh, do things, and stuff!")
            return random.randint(30,120)
            
        # Let the One WOrd Story start!
        start_line = random.choice(startup_lines)
        await ctx.send("Alright, lets begin! I'll go first: \n{}".format(start_line))
        await asyncio.sleep(3)
        start_line = start_line.strip(".")
        #start_line = start_line.strip('"')
        
        begin = datetime.datetime.now()
        current = begin
        # COOLDOWN TIMEOUT WHATEVER
        timeout_value = await self.config.guild(ctx.guild).get_raw('Round_time')
        user_cd = await self.config.guild(ctx.guild).get_raw('Answer_time')
        cd_users = list()
        maxwordcount = await self.config.guild(ctx.guild).get_raw('Max_words')
        wordcount = 0
        
           
        
        while True:
            
            #async def end_function():
               
                
        
            """if(maxwordcount==10):
                start_line += "."
                counter += 1
                delmessage = await ctx.send("Let's see what we got here...")
                await asyncio.sleep(3)
                await delmessage.delete()
            
                embed = discord.Embed(
                    colour=ctx.guild.me.top_role.colour,
                    title = "One Word Story #{}".format(counter),
                    description = ('{}').format(start_line)
                    )
                
                await ctx.send(embed=embed)
                await self.config.guild(ctx.guild).set_raw('Counter', value = counter)
                return 0"""
            
            try:
                wordlength = random.randint(8,22)
                
                # PICK CODE 1
                chosen_user = None
                while(True):
                    try:
                        tempuser = random.choice(join_users)
                        cd_users.append(tempuser)
                        join_users.remove(tempuser)
                        break
                    
                    except IndexError:
                        join_users = cd_users
                        cd_users = list()
                        tempuser = random.choice(join_users)
                   
                    
                # START OF WORD-ADDING
                wordmsg = await ctx.send("Alright {}, give me a word no longer than {} letters!".format(tempuser.mention, wordlength))
                
                current = datetime.datetime.now()
                current=(timeout_value - (current-begin).seconds)
                
                if current < user_cd: 
                    user_cd = current
                
                while True:
                    message = await self.bot.wait_for('message',
                                                  timeout=user_cd, check=usercheck)
                                                        
                    if(message.author is tempuser):
                        content = message.content
                        if not len(content.split())>1:
                            if len(content) <= wordlength:
                                message.delete()
                                content.strip(' ')
                                start_line += " " + content
                                wordcount += 1
                                break
                                
                            else:
                                await ctx.send("Word too long!")
                        else:
                            await ctx.send("Only one word!")
                        
                        
                        
                    message.delete()
            # Either stops the game or goes to the next user.
            except asyncio.TimeoutError:
                current = datetime.datetime.now()
                timer=(timeout_value - (current-begin).seconds)
                
                lastmessageiter = discord.abc.Messageable.history(ctx.channel, limit=1)
                async for message in lastmessageiter:
                    await message.delete()
                # IF TIMER
                if timer <= 0:
                    start_line += "."
                    # PICK CODE 2
                    """chosen_user = None
                    while(True):
                        try:
                            tempuser = random.choice(join_users)
                            cd_users.append(tempuser)
                            join_users.remove(tempuser)
                            break
                        
                        except IndexError:
                            join_users = cd_users
                            cd_users = list()
                            tempuser = random.choice(join_users)
                            
                    
                    wordmsg = await ctx.send("We need a title for this masterpiece! {}, what should it be? Max 30 letters.!".format(tempuser.mention))
                    
                    while(True):
                    
                        message = await self.bot.wait_for('message',
                                                      timeout=17, check=usercheck)"""
                        
                    counter += 1
                    delmessage = await ctx.send("Let's see what we got here...")
                    await asyncio.sleep(3)
                    await delmessage.delete()
                
                    embed = discord.Embed(
                        colour=ctx.guild.me.top_role.colour,
                        title = "One Word Story #{}".format(counter),
                        description = ('{}').format(start_line)
                        )
                    
                    await ctx.send(embed=embed)
                    channel = self.bot.get_channel(477039773551296522)
                    await channel.send(embed=embed)
                    await self.config.guild(ctx.guild).set_raw('Counter', value = counter)
                    print("We got to almost the end")
                    return 1
                    """start_line += "."
                    counter += 1
                    delmessage = await ctx.send("Let's see what we got here...")
                    await asyncio.sleep(3)
                    await delmessage.delete()
                
                    embed = discord.Embed(
                        colour=ctx.guild.me.top_role.colour,
                        title = "One Word Story #{} <@&476900791475634187>".format(counter),
                        description = ('{}').format(start_line)
                        )
                    
                    await ctx.send(embed=embed)
                    await self.config.guild(ctx.guild).set_raw('Counter', value = counter)
                    return 0"""
                    
                else:
                    await ctx.send("Time out! Next user!")
                    cd_users.append(message.author)

    #async def get_random_person(join_users, cd_users):
        
                
        #return tempuser, join_users, cd_users
