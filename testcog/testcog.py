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
import codecs
import io

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


class TestCog:


    def __init__(self, bot):
        self.tasks = []
        self.bot = bot
        self.config = Config.get_conf(self, 8358350000, force_registration=True)

        
        # self.config.register_guild(**ows_defaults)
        
    q_dict = {}   
   
    """@commands.command()   
    async def ertest(self, ctx):
        path = bundled_data_path(self) / 'data.json'
        #path = '/home/redbot/Documents/json.json'
        with open(path, encoding="utf8") as f:
            data = json.load(f)
        return data"""


    @commands.command()
    async def dtest(self, ctx):
        msg = await ctx.send("Eta mat")
        await msg.pin()

        async for message in ctx.history(limit=3):
                if message.content != msg.content and message.author == self.bot.user:
                    await message.delete()

    @commands.command()
    async def stest(self, ctx):
        string = "12345"
        nstring = string[:-1]
        await ctx.send(nstring)
        await ctx.send(ctx.author.display_name)

        
        
    @commands.command()
    async def rotest(self, ctx):
        num = 3.1212121212121
        num = round(num,2)
        await ctx.send(num)