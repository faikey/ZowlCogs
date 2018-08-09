import discord
from discord.ext import commands
from redbot.core import Config, bank
import random
import time

class Cooldowns:

    
    
    def __init__(self):
        self.config = Config.get_conf(self, 8358350000, force_registration=True)
        
        cooldowns = {"cooldowns": {
        "Safe": 345600,
        "Rob": {
            "utu": 10800,
            "base": 1800
                },
        "Events":{
            "Questions": 13},
        "One_Word_Story": 700
            }
        }
        
        self.config.register_guild(**cooldowns)
        
        
    #user arg should be user ID
    async def start_cooldown(self, ctx, user, feature):
        self.gconf = self.config.guild(ctx.guild)

        timenow = int(time.time())
        
        userid = ctx.author.id
        
        if(feature is "Safe"):
            safe_cooldown = await self.gconf.get_raw('cooldowns', 'Safe')
            newtime = timenow + safe_cooldown
            await self.gconf.set_raw(userid, 'cooldowns', 'safe', value = newtime)
        
        if(feature is "Rob"):
            rob_utu_cooldown = await self.config.get_raw('cooldowns', 'Rob', 'utu')
            rob_base_cooldown = await self.config.get_raw('cooldowns', 'Rob', 'base')

            newtime_utu = timenow + int(rob_utu_cooldown)
            newtime_base = timenow + int(rob_base_cooldown)
            await self.gconf.set_raw(userid, 'cooldowns', 'Rob','utu', user, value =  newtime_utu)
            await self.gconf.set_raw(userid, 'cooldowns', 'Rob','base', value = newtime_base)
            
        if feature is 'Events':
            events_questions_cooldown = await self.gconf.get_raw('cooldowns', 'Events', 'Questions')
            newtime = timenow + safe_cooldown
            await self.gconf.set_raw(userid, 'cooldowns', 'safe', value = newtime)
    
    
    async def get_default_cooldown(self, ctx, feature, subfeature=None):
        cooldowns = await self.config.guild(ctx.guild).cooldowns.all()
        cooldowns = cooldowns
        print(cooldowns)
        
        if feature == 'Events':
            if subfeature == 'Questions':
                return cooldowns['Events']['Questions']
        
        return cooldowns[feature]

    #user arg should be an id not an object
    
    # Proposal to merge this into a more general function, e.g get_current_cooldown
    async def get_rob_utu_cooldown(self, ctx, user):
        self.gconf = self.config.guild(ctx.guild)

        try:
            cooldown_time = await self.gconf.get_raw(ctx.author.id, 'cooldowns', 'Rob', 'utu', user)
            remaining = int(cooldown_time) - int(time.time())

            if remaining <= 0:
                return None
            else:
                return await self.display_sec(remaining)

        except KeyError:
            return None



    async def get_current_cooldown(self, ctx, feature, user: discord.Member=None):
        #if user is None:
        user = ctx.author
        userid = ctx.author.id
        #else:
         #   user.id = ctx.user.id
         

         
        self.gconf = self.config.guild(ctx.guild)
        try:
            cooldowntime = await self.gconf.get_raw(userid, 'cooldowns', feature)
            remainder = 1 + cooldowntime - int(time.time())
        except KeyError:
            await self.gconf.set_raw(userid, 'cooldowns', feature, value = 0)
            return remainder
        # await ctx.send("{} gas a cooldown of {}.".format(feature,cooldown)
     
    @commands.command()
    async def show_cooldown(self, ctx, feature, user: discord.Member=None):
        await ctx.send("test")
        cooldown = await self.get_current_cooldown(ctx, feature, user)
        if cooldown is None:
            cooldown = 0

        cooldown = display_sec(cooldown)

        await ctx.send("{} has a cooldown of {}.".format(feature,cooldown))
    
    async def display_sec(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        #this can be optimized, refactor at some point
        if seconds is None:
            return str(0)

        if seconds <= 0:
            return str(0)

        if seconds < 60:
            return str(seconds)

        if seconds >= 3600:
            return '**' + str(h) + '** hour(s) **' + str(m) + '** minute(s) and **' + str(s) + '** second(s)'
        
        if seconds >= 60:
             return '**' + str(m) + '** minute(s) and **' + str(s) + '** second(s)'


      

    @commands.command()
    async def testx(self, ctx):
        await ctx.send("Yes I'm alive")
        
        
