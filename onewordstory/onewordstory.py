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
        
     
     
        ows_defaults = {'Cooldown': 10800,
                            'Counter': 0,
                            'Round_time': 100,
                            'Start_time': 60,
                            'Answer_time': 14,
                            'Max_words': 40
                            }
                            
        # If releasing, make sure to change the channel ID. Can be an available command with e.g set_channel
        
        self.config.register_guild(**ows_defaults)
        

    def __unload(self):
        for task in self.tasks:
            task.cancel()
     
    @checks.is_owner()       
    @commands.command()    
    async def ows_l(self,ctx):
        """Loops One Word Story in the current channel!"""
        self.tasks.append(self.bot.loop.create_task(self.ows_loop(ctx)))
        #await self.ows_loop(ctx)
    
    async def ows_loop(self, ctx):
        # while self.bot.get_cog('OneWordStory') is self:
        while self == self.bot.get_cog("OneWordStory"):
            # Gets any cooldownadd from the ows_function as 'cooldownadd' as well as getting the default cooldown for "One Word Story" from the cooldowns cog.
            cooldownadd, delmsgs = await self.ows_function(ctx)
            #cooldowns = ctx.bot.get_cog('Cooldowns')
            #cooldown = await cooldowns.get_default_cooldown(ctx, 'One_Word_Story')
            cooldown = await self.config.guild(ctx.guild).get_raw('Cooldown')
            
            
            minutenumber = int(cooldown / 60)
            
            # Returns a string with what the output should say.
            def time_output_creation(minutes):
                hours  = int(minutes/60)
                minutes = minutes-hours*60

                suboutput = "**{}** minutes".format(minutes)

                if hours > 0:
                    suboutput = "**{}** hours and {}".format(hours, suboutput)

                return "I'll host a new round of One Word Story in {}.".format(suboutput)

            # Send the initial message.
            delmsg = await ctx.send(time_output_creation(minutenumber))
            
            #pinmsg = bot.loop.create_task(coro_function(argument))
            
            for message in delmsgs:
                await message.delete()
            await delmsg.pin()
            # Deletes pin msg.
            async for message in ctx.history(limit=1):
                await message.delete()

            cooldownminus = 0

            # At the time of creation of this cog, the only instance of events to return a value is if nobody responds to Chip. In this case, he will delete 3/4 out
            # of the last messages sent. This is set up for that nobody else writes in the 12 second window before it disappears, could be changed
            # later. Is there to reduce spam.
            """if cooldownadd > 1:
                await asyncio.sleep(12)
                forcounter = 0
                async for message in ctx.history(limit=1):
                    await message.delete()
                async for message in ctx.history(limit=3, reverse=True):
                    forcounter += 1
                    if forcounter < 3:
                        await message.delete()

                cooldownminus = 12"""

            # Counts down the time until the next OWS.
            for i in range(minutenumber):
                i += 1
                await asyncio.sleep(60)
                await delmsg.edit(content=(time_output_creation(minutenumber-i)))
            
            
            await delmsg.delete()
            
        await ctx.send("We didn't loop?")
        
   
    """@commands.command()
    async def iter(self,ctx):
        lastmessageiter = discord.abc.Messageable.history(ctx.channel, limit=3)
        await iterfunc()
        
        async def iterfunc():
            async for message in lastmessageiter:
                await message.delete()
                
    @commands.command()
    async def siter(self,ctx):
        async for message in ctx.history(limit=3):
            await message.delete()
 
    @commands.command()
    async def ftest(self,ctx):
        def checkman():
            return True
            
        if checkman():
            print("YEAH BABY")
    @commands.command()
    async def embtest(self,ctx):
        embed = discord.Embed(
                        colour=ctx.guild.me.top_role.colour,
                        title = "potet",
                        description = "potet"
                        )
        await ctx.send(embed=embed)
        embed = embed.to_dict()
        print(embed)
        newembed = discord.Embed(**embed)
        await ctx.send(embed=newembed)
        ## NICE!"""
 
    async def ows_function(self, ctx):

        ows_values = {
                    "Games":{
                        "One Word Story":
                            {},
                        "Song":{
                            "Start": "It's time to make a song!"
                            }
                        }
                    }
    
        startup_lines = ["Did you hear of the...", "There once was a...", '"Morty, we gotta...',
                        "The old man from...","Somebody once told me...", "The universe is...",
                        "The fact of the matter is...", "Did you know that...", "Fyre makes soap out of...",
                        "The FBI doesnt know yet but...", "After a long talk my roommates and I decided that...",
                        "My father used to always say...",  "Your mother is...",
                        "Have you ever wondered about...", "Sorry I was late boss, I...", "Mom, it's not what it looks like. I was just...",
                        "One thing that people dont understand is...", "As a licensed professional I think that...",
                        "\"What are you doing?\" Don't worry I was just...", "When you look at it from a technical standpoint...", 
                        "Did you know that its illegal to...", "I watch Rick and Morty because..."]
        sad_lines = ["Oh. Well, I uh, I had better things to do anyways! Like uh, do things, and stuff! *By myself...*", "Hello? Nobody? No...?",
                     "Play with me, damnit! I refuse to go back to the butter-passing factory!", "Oh nobody? Bah, I guess you are all busy." \
                     " Or sick. Or dead. *Hopefully dead...*","**ECHO**,**echo**, echo, *echo*...",
                     "What music do I listen to? Good question, human who is actually my friend and actually exists. Thanks"\
                     " for not leaving me hanging here!  \n\n :'("]
        
        #game_name = random.choice(ows_values.keys())
        game_name = "One Word Story"

        # Counts the number of OWSes.
        try:
            counter = await self.config.guild(ctx.guild).get_raw(game_name,'Counter')
        except KeyError:
            counter = await self.config.guild(ctx.guild).set_raw(game_name, 'Counter', value = 1)

        def usercheck(message):
            return message.author != self.bot.user and message.channel.id == ctx.channel.id
        
        join_users = list()
        begin = datetime.datetime.now()
        current = begin
        start_time = await self.config.guild(ctx.guild).get_raw('Start_time')
        role =  discord.utils.get(ctx.guild.roles,id=476900791475634187)
        await role.edit(mentionable=True)
        start_msg = await ctx.send("<@&476900791475634187>\n✎ **ONE WORD STORY TIME!** 📖\nBeep boop, Chip here! It's time to play 'One Word Story!' Type **ows** in the chat to join! We start in {} seconds!".format(start_time))
        await role.edit(mentionable=False)
        delmsgs = []
        delmsgs.append(start_msg)
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
                
                # await message.delete()
                
        except asyncio.TimeoutError:
            pass
        
        if not join_users:
            stop_line = random.choice(sad_lines)
            delmsg = await ctx.send(stop_line)
            delmsgs.append(delmsg)
            return 1, delmsgs
            # return random.randint(30, 120)
            
        # Let the One WOrd Story start!
        start_line = random.choice(startup_lines)
        await ctx.send("Alright, lets begin! I'll go first: \n**{}**".format(start_line))
        await asyncio.sleep(3)
        start_line = start_line.strip(".")
        #start_line = start_line.strip('"')
        
        # Takes user input on a cycle.
        start_line = await self.take_input(ctx, join_users, start_line)

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
        # FIX THIS
        #channel = ctx.channel
        channel = self.bot.get_channel(477039773551296522)
        await channel.send(embed=embed)
        await self.config.guild(ctx.guild).set_raw(game_name, 'Counter', value = counter)
        # Saves the newest OWS.
        embed_dict = embed.to_dict()

        await self.save_ows_embed(ctx, join_users, embed_dict, counter, game_name)
        newdelmsg = await ctx.send("Round finished!")
        delmsgs.append(newdelmsg)
        return 1, delmsgs
            

    async def save_ows_embed(self, ctx, participants, embed_dict, counter, game_name):
        self.gconf = self.config.guild(ctx.guild)
        participants = [member.id for member in participants]
        await self.gconf.set_raw(game_name, counter, "Embed",value=embed_dict)
        await self.gconf.set_raw(game_name, counter, "Participants",value=participants)
        await self.gconf.set_raw(game_name, counter, "Timestamp",value=int(time.time()))

    async def take_input(self, ctx, join_users, start_line):

        def usercheck(message):
            return message.author != self.bot.user and message.channel.id == ctx.channel.id

        begin = datetime.datetime.now()
        current = begin
        # COOLDOWN TIMEOUT WHATEVER
        timeout_value = await self.config.guild(ctx.guild).get_raw('Round_time')
        user_cd = await self.config.guild(ctx.guild).get_raw('Answer_time')
        all_users = join_users[:] # Optionally join_users.copy()
        cd_users = list()
        maxwordcount = await self.config.guild(ctx.guild).get_raw('Max_words')
        wordcount = 0

        while True:
            
            # Picks a random user that's not "on cooldown", and if there are no available users, resets the "cooldown" of all the users.
            try:
                
                wordlength = 25
                # Picks a random user.
                tempuser = None
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
                   
                current = datetime.datetime.now()
                current=(timeout_value - (current-begin).seconds)

                # START OF WORD-ADDING
                wordmsg = await ctx.send("*{}*...\nAlright {}, give me a word! *{} seconds remaining...*".format(start_line, tempuser.mention, current))
                
                

                # User timer is a set number, but if the overall cooldown is below the user timer, then that is the new timeout value.
                if current < user_cd: 
                    user_cd = current
                
                while True:
                    message = await self.bot.wait_for('message',
                                                  timeout=user_cd, check=usercheck)
                                                        
                    if(message.author is tempuser):
                        content = message.content
                        if not len(content.split())>1:
                            if len(content) <= wordlength:
                                content.strip(' ')
                                start_line += " " + content
                                wordcount += 1
                                break
                                
                            else:
                                await ctx.send("Word too long!")
                        else:
                            await ctx.send("Only one word!")
                    
            # Either stops the game or goes to the next user.
            except asyncio.TimeoutError:
                current = datetime.datetime.now()
                timer=(timeout_value - (current-begin).seconds)
                
                
                # IF TIMER
                if timer <= 0:
                    return start_line

                else:
                    await ctx.send("Time out! Next user!")
                    #cd_users.append(tempuser)
                    """if usercheck(message):
                        cd_users.append(message.author)"""

    
