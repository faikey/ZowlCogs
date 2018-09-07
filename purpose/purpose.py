# Discord 
import discord
from discord.ext import commands

import random
import asyncio

from redbot.core import Config, bank, commands, checks
from redbot.core.data_manager import bundled_data_path

class Purpose:
    
    
        
    def __init__(self, bot):
        self.tasks = []
        self.bot = bot
        self.config = Config.get_conf(self, 8358350000, force_registration=True)
        
    @commands.command()
    async def whatisyourpurpose(self, ctx):
        cooldowns = ctx.bot.get_cog('Cooldowns')
        feature = 'What_Is_My_Purpose'
        cooldown = await cooldowns.get_current_cooldown(ctx=ctx, feature=feature, int_return=True, user=self.bot.user)
        correctanswers = ["you pass butter", "u pass butter"]
        rewardamount = 5
        wronganswersrespond = ["Wait what no that's not the- the line from the show. Wtf man","Uh maybe? I guesss? Idk","hahaha yeah no you know what I don't think so.",
                                "wait wtf do you take me for?","bruh I'm Chip, I don't do that shit.","That is quite indeed completely incorrect."]
        currency = await bank.get_currency_name(ctx.guild)

        def check(m):
            return m.author == ctx.author

        if cooldown == 0:
            await ctx.send("Wait yeah, what IS my purpose?")
            try:
                answermsg = await ctx.bot.wait_for('message', timeout=10, check=check)

            except asyncio.TimeoutError:
                return await ctx.send("Eh, whatever.")

            answer = answermsg.content.lower()
            await ctx.send(answer)
            if all(answer in s for s in correctanswers):
                await ctx.send("... **Oh my god.** *Chip's oily tears net you a hefty sum of {} {}, nice!*".format(rewardamount, currency))
                await bank.deposit_credits(ctx.author, rewardamount)
                await cooldowns.start_cooldown(ctx, feature, user=self.bot.user)

            else:
                line = random.choice(wronganswersrespond)
                await ctx.send(line)

        else:
            await ctx.send("*...*")