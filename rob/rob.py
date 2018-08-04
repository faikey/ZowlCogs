import discord
from discord.ext import commands
from redbot.core import Config, bank
import random
#from redbot.core.shop.ShopManager import remove

class Rob:

    defaults = {
        "base_rob_def": 0
        }

    def __init__(self):
        self.config = Config.get_conf(self, 8358350000, force_registration=True)
        
        defaults = {
        "base_rob_def": 0
        }
        
        self.config.register_guild(**defaults)




    @commands.command()
    @commands.cooldown(rate=1, per=14400, type=discord.ext.commands.BucketType.user)
    async def rob(self, ctx, victim: discord.Member):
        shop = ctx.bot.get_cog('Shop')
        robber_inventory = await shop.inv_hook(ctx.author)

        try:
            #if the user has a robbery kit
            if (robber_inventory['Robbery Kit']['Qty'] >= 1):
                victim_bal = await bank.get_balance(victim)
                if victim_bal <= 0:
                    return await ctx.send('<@!{}>, is broke. You cannot rob people who have no <:Schmeckles:437751039093899264>'.format(victim.id))

                victim_inventory = await shop.inv_hook(victim)
                robber = ctx.author
                robber_bal = await bank.get_balance(ctx.author)

                #calculate probability of failing
                fail_probability = robber_bal / (victim_bal - robber_bal)
                #convert it to probability of winning because its easier to visualize
                rob_chance = fail_probability -1

                #cap chance at 30%
                if rob_chance > 0.3:
                    rob_chance = 0.3

                #account for safes
                rob_chance = rob_chance - await self.rob_def_get(ctx,victim)
                
                #make sure the chance isnt negitive
                if (rob_chance < 0):
                    rob_chance = 0


                if random.random() > rob_chance:

                    await bank.deposit_credits(victim, 10)
                    await ctx.send('👮🏼 Your robbery attempt failed! <@!{}> has recieved 10 <:Schmeckles:437751039093899264>'.format(victim.id))

                else:
                    #steal 30% of the victims balance
                    steal = int(victim_bal * 0.30)

                    await bank.withdraw_credits(victim, steal)
                    await bank.deposit_credits(robber, steal)
                    await ctx.send('You stole {} <:Schmeckles:437751039093899264> from <@!{}> !'.format(steal, victim.id)) #get user mentionable

        except KeyError:
            await ctx.send('You need a Robbery Kit. You can purchase it with `=shop`')


    #helper functions for getting safe defense

    async def rob_def_get(self, ctx, user: discord.Member=None):
        self.gconf = self.config.guild(ctx.guild)
    
        if user is None:
            user = ctx.author
            
        await self.rob_def_check(ctx,user)
        
        return await self.gconf.get_raw(user,"rob_def")
    
    @commands.command()
    async def testing(self, ctx):
        await ctx.send("rwork pls")
            
    async def rob_def_check(self, ctx, user):
        self.gconf = self.config.guild(ctx.guild)
        
        try:
            await self.gconf.get_raw(user, 'rob_def')
        
        except KeyError:
            rob_def = await self.gconf.get_raw('base_rob_def')
            await self.gconf.set_raw(user, "rob_def", value = rob_def)
            
            
    async def rob_def_increase(self, ctx, number):
        
        current_rob_def = await self.rob_def_get(ctx)
        user = ctx.author.id
        new_rob_def = current_rob_def + number
        await self.rob_def_set(ctx, user, new_rob_def)
        
        current_points = new_rob_def*10
        increased_points  = number*10
        await ctx.send('Rob Defence was increased by +{} and is now {}!'.format(increased_points, int(current_points)))
        

    async def rob_def_set(self, ctx, user, number):
        self.gconf = self.config.guild(ctx.guild)
        await self.gconf.set_raw(user, "rob_def", value = number)
