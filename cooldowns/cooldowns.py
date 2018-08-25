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
            "Questions": 20},
        "One_Word_Story": 600
            }
        }
        
        self.config.register_guild(**cooldowns)
        
        
    """
    starts a cooldown for a given feature

    Args:
        ctx: context of what caused the cooldown (discord message object)
        feature: name of the feature that is being cooled down (string, "Safe", "Rob", or "Events")
        user: optional argument that specifies the user being robbed (int, discord members ID)


    """
    async def start_cooldown(self, ctx, feature, user=None):
        self.gconf = self.config.guild(ctx.guild)

        timenow = int(time.time())
        userid = ctx.author.id
        
        if feature is 'Safe':
            #safe_cooldown = await self.config.get_raw('cooldowns', 'Safe')
            safe_cooldown = await self.get_default_cooldown(ctx, feature)
            newtime = timenow + safe_cooldown
            await self.gconf.set_raw(userid, 'cooldowns', 'Safe', value=newtime)
        
        if feature is 'Rob':
            rob_utu_cooldown = await self.config.get_raw('cooldowns', 'Rob', 'utu')
            rob_base_cooldown = await self.config.get_raw('cooldowns', 'Rob', 'base')

            newtime_utu = timenow + int(rob_utu_cooldown)
            newtime_base = timenow + int(rob_base_cooldown)
            await self.gconf.set_raw(userid, 'cooldowns', 'Rob','utu', user, value=newtime_utu) 
            await self.gconf.set_raw(userid, 'cooldowns', 'Rob','base', value=newtime_base)
            
        if feature is 'Events':
            events_questions_cooldown = await self.gconf.get_raw('cooldowns', 'Events', 'Questions')
            newtime = timenow + events_questions_cooldown
            await self.gconf.set_raw(userid, 'cooldowns', 'safe', value=newtime)
    


    """
    gets the default cooldown for a given feature or subfeature

    Args:
        ctx: context
        feature: name of the feature to get the cooldown from (string, "Safe", "Rob", or "Events")
        subfeature: optional argument 


    """
    async def get_default_cooldown(self, ctx, feature, subfeature=None):
        cooldowns = await self.config.guild(ctx.guild).cooldowns.all()
        cooldowns = cooldowns
        """print("Cooldowns yo")
        print(cooldowns)"""
        
        if subfeature is not None:
            return cooldowns[feature][subfeature]
        else:
            return cooldowns[feature]



    """
    gets the cooldown of a given user for a given feature

    Args:
        ctx: context of what caused the cooldown check (discord message object)
        feature: name of the feature to get the cooldown from (string, "Safe", "Rob", or "Events")
        user: ID of user to check cooldown (int, discord members ID)
        int_return: optional argument that returns the cooldown remainder in seconds instead of a string (bool, default:false)
        subfeatures: list of subfeatures to decend into, eg: ['utu','233669548673335296']. This would be the same as get_raw(..., 'utu', '233669548673335296')

    Returns:
        a string containing the time remaining. eg: 2 hours 15 minutes 47 seconds remaining. This can be changed to just seconds with the int_return argument
        OR returns 0 if the cooldown has expired or the user never had a cooldown in the first place
    """
    async def get_current_cooldown(self, ctx, feature, user, subfeatures=None, int_return=False):
        self.gconf = self.config.guild(ctx.guild)

        try:
            if subfeatures is not None:
                cooldowntime = await self.gconf.get_raw(ctx.author.id, 'cooldowns', feature, 'utu', user)
            else:
                cooldowntime = await self.gconf.get_raw(ctx.author.id, 'cooldowns', feature)

            remainder = cooldowntime - int(time.time())

            if remainder < 0:
                #if the cooldown has expired
                return 0
            else:
                if (int_return):
                    return remainder
                else:
                    return await self.display_sec(remainder)

        except KeyError:
            return 0
     


    #show_cooldown function has been removed as it can be handled by get_current_cooldown 


    """
    internal function that converts seconds to a human friendly format

    Args:
        seconds: int

    Returns:
        string

    eg: display_sec(11747) would return "3 hours 15 minutes and 47 seconds"

    """
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