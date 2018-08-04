import discord
from discord.ext import commands
from redbot.core import Config, bank
import random
#from redbot.core.shop.ShopManager import remove

class Test:
    def __init__(self):
        self.config = Config.get_conf('Shop', 5074395003, force_registration=True)




    @commands.command()
    #@commands.cooldown(rate=1, per=14400)
    async def rob(self, ctx, victim: discord.Member):
        shop = ctx.bot.get_cog('Shop')
        robber_inventory = await shop.inv_hook(ctx.author)

        try:
            if (robber_inventory['Robbery Kit']['Qty'] >= 1):

                victim_inventory = await shop.inv_hook(victim)
                victim_bal = await bank.get_balance(victim)
                robber = ctx.author
                robber_bal = await bank.get_balance(ctx.author)

                fail_probability = robber_bal / (victim_bal - robber_bal)

                probability = fail_probability -1

                if probability > 0.7:
                    probability = 0.7

                safe_probability = 0

                try:
                    #add more safes
                    if victim_inventory['Blue Safe']:
                        safe_probability = 0.3
                except KeyError:
                    pass

                try:
                    #add more safes
                    if victim_inventory['Yellow Safe']:
                        safe_probability = 0.4
                except KeyError:
                    pass

                try:
                    #add more safes
                    if victim_inventory['Red Safe']:
                        safe_probability = 0.5
                except KeyError:
                    pass


                probability = probability - safe_probability

                if (probability < 0):
                    probability = 0

                if random.random() < probability:

                    await bank.withdraw_credits(ctx.author, 10)
                    await bank.deposit_credits(victim, 10)

                    fine = 10

                    await ctx.send('👮🏼 Your robbery attempt failed! <@!{}> has recieved 10 <:Schmeckles:437751039093899264>'.format(victim.id))
                    #remove safe cracking tools from inventory

                else:

                    steal = int(victim_bal * 0.30)

                    await bank.withdraw_credits(victim, steal)
                    await bank.deposit_credits(robber, steal)
                    await ctx.send('You stole {} <:Schmeckles:437751039093899264> from <@!{}> !'.format(steal, victim.id)) #get user mentionable



        except KeyError:
            await ctx.send('You need a Robbery Kit. You can purchase it with `=shop`')






    async def cb(self, ctx, item):

        print('callback')
        print(ctx)
        shop = ctx.bot.get_cog('Shop')
        inventory = await shop.inv_hook(ctx.author)

        author = ctx.author
        """Converts gold item to credits."""
        try:
            if (inventory['Gold Bar']['Qty'] >= 1):
                """Removes gold bar."""
                """insert remove here"""

                currency = await bank.get_currency_name(ctx.guild)
                bal = await bank.get_balance(author)
                goldworth = 100
                newbal = bal + goldworth

                await bank.set_balance(author, newbal)
                await ctx.send("You traded a Gold bar for {} {}! \nYou now have {} {}!".format(goldworth,currency,newbal,currency))
        except AttributeError:
            await ctx.send("You don't have a gold bar!")
        except KeyError:
            await ctx.send("You don't have a gold bar!")


