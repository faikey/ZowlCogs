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

# Others
import asyncio
import datetime
import random


class LiveLeaderboard:


    def __init__(self, bot):
        self.tasks = []
        self.bot = bot
        self.config = Config.get_conf(self, 8358350000, force_registration=True)

        
        # self.config.register_guild(**ows_defaults)
        

    def __unload(self):
        for task in self.tasks:
            task.cancel()
     
    @commands.command()   
    async def xtest(self, ctx):
        #"""economy = ctx.bot.get_cog('Economy')
        #await economy.leaderboard(ctx)"""
        await ctx.send("=leaderboard")
     
    """@checks.is_owner()       
    @commands.command() 
    async def ows_l(self,ctx):
       self.tasks.append(self.bot.loop.create_task(self.ows_loop(ctx)))
    
    async def ows_loop(self, ctx):
        pass"""
        