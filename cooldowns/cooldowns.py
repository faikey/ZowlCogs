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
            "utu": 3600,
            "base": 3600
                }
            }
        }
        
        self.config.register_guild(**cooldowns)
        
        
        
        
    async def start_cooldown(self, ctx, user, feature):
        self.gconf = self.config.guild(ctx.guild)
        timenow = int(time.time())
        
        userid = ctx.author.id
        
        if(feature is "Safe"):
            safe_cooldown = await self.gconf.get_raw('cooldowns', 'Safe')
            newtime = timenow + safe_cooldown
            await self.gconf.set_raw(userid, 'cooldowns', 'safe', value = newtime)
        
        if(feature is "Rob"):
            rob_utu_cooldown = await self.gconf.get_raw('cooldowns', 'rob', 'utu')
            rob_base_cooldown = await self.gconf.get_raw('cooldowns', 'rob', 'base')
            newtime_utu = timenow + rob_utu_cooldown
            newtime_base = timenow + rob_base_cooldown
            await self.gconf.set_raw(userid, 'cooldowns', 'rob','utu', value =  newtime_utu)
            await self.gconf.set_raw(userid, 'cooldowns', 'rob','base', value = newtime_base)
    
    
    async def get_cooldown(self, ctx, feature, user: discord.Member=None):
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
        cooldown = await self.get_cooldown(ctx, feature, user)
        await ctx.send("{} gas a cooldown of {}.".format(feature,cooldown))
    
    @commands.command()
    async def testx(self, ctx):
        await ctx.send("Yes I'm alive")
        
        