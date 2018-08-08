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
        self.bot = bot
        self.config = Config.get_conf(self, 8358350000, force_registration=True)
     
     
        ows_defaults = {'Cooldown': 30,
                            'Counter': 0
                            }
                            
        self.config.register_guild(**ows_defaults)
     
    @commands.command()
    async def iter(self,ctx):
        lastmessageiter = discord.abc.Messageable.history(ctx.channel, limit=3)
        await iterfunc()
        
        async def iterfunc():
            async for message in lastmessageiter:
                await message.delete()
    @checks.is_owner()       
    @commands.command()
    async def ows_loop(self, ctx):
        #while self.bot.get_cog('OneWordStory') is self:
        while True:
            await self.ows_function(ctx)
            await asyncio.sleep(180)
        await ctx.send("We didn't loop?")
        
     
 
    async def ows_function(self, ctx):
    
        startup_lines = ["Did you hear of the...", "There once was a...", '"Morty, we gotta...', "The old man from..."]
        
        try:
            counter = await self.config.guild(ctx.guild).get_raw('Counter')
        except KeyError:
            counter = await self.config.guild(ctx.guild).set_raw('Counter', value = 1)

        def usercheck(message):
            return message.author != self.bot.user
        
        join_users = list()
        begin = datetime.datetime.now()
        current = begin
        timeout_value = 50
        
        await ctx.send("**ONE WORD STORY TIME!**\nBeep boop, Chip here! It's time to play 'One Word Story!' Type **ows** in the chat to join! We start in 20 seconds!")
        
        # Adds users who type "ows" into a list.
        try:
            while True:
                current = datetime.datetime.now()
                message = await self.bot.wait_for('message',
                                              timeout=(timeout_value - (current-begin).seconds),check=usercheck
                                              )
                if message.author not in join_users and message.content.lower() == 'ows':
                    join_users.append(message.author)
                    await ctx.send("{} joined!".format(message.author.mention))
                
                message.delete()
                
        except asyncio.TimeoutError:
            pass
        
        if not join_users:
            delmsg = await ctx.send("Oh. Well, I uh, I had better things to do anyways then play games! Like uh, do things, and stuff!")
            return
            
        # Let the One WOrd Story start!
        start_line = random.choice(startup_lines)
        await ctx.send("Alright, lets begin! I'll go first: \n{}".format(start_line))
        await asyncio.sleep(3)
        start_line = start_line.strip(".")
        start_line = start_line.strip('"')
        
        begin = datetime.datetime.now()
        current = begin
        timeout_value = 10
        user_cd = 15
        cd_users = list()
        messagecount = 0
        
           
        
        while True:
            if(messagecount==10):
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
                return
            
            try:
                wordlength = random.randint(5,15)
                chosen_user = None
                while(True):
                    print("pasta2")
                    try:
                        tempuser = random.choice(join_users)
                        cd_users.append(tempuser)
                        join_users.remove(tempuser)
                        break
                    
                    except IndexError:
                        join_users = cd_users
                        cd_users = list()
                        tempuser = random.choice(join_users)
                    """counter += 1
                    if counter == join_users:"""
                    
                       
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
                            if len(content) < wordlength:
                                message.delete()
                                cd_users.append(message.author)
                                content.strip(' ')
                                start_line += " " + content
                                messagecount += 1
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
                if timer <= 0:
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
                    return
                    
                else:
                    await ctx.send("Time out! Next user!")
                    cd_users.append(message.author)
        
       
