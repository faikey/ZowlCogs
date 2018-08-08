
    # HOW TO PRINT ROLES
    @commands.command()
    async def testt(self,ctx):
        print(ctx.guild.roles)
        print(ctx.author.roles)
        
        #WORKS!
    @commands.command()
    async def etest(self,ctx):
        number=1
        embed = discord.Embed(
                title = 'React to 1',
                description = '--> {} <--'.format(number)
            )
        message = await ctx.send(embed=embed)
        await asyncio.sleep(1)
        number=2
        await message.edit(embed=discord.Embed(description = number))
        
    @commands.command()
    async def qtest(self,ctx):
    
        def check(number):
            return isinstance(int(number.content), int)
    
        await ctx.send("Write 1:")
        
        
        try:   
            doneit = False
            while(not doneit):
                message = await ctx.bot.wait_for(
                    "message", check=check, timeout=5.0                
                )
                if int(message.content) == 1:
                    doneit = True
                    
            await ctx.send("GJ BRO!")
    
            
        except asyncio.TimeoutError:
             await ctx.send("Skriv 1 3 ganger:")
    
    
        
    @commands.command()
    async def gettest(self, ctx):
    
        self.gconf = self.config.guild(ctx.guild)
        
        print("HEI JARLEE")
        await self.gconf.set_raw('test', value={'othertest':{}} )
        await self.gconf.set_raw('test','othertest', value="testval")
        dicty = await self.gconf.get_raw('test','othertest')
        printy = await self.gconf.get_raw('Questions')
        print(dicty)
        #await ctx.send(dict)   
        #await ctx.send(printy)          
    
    @commands.command()
    async def qutest(self,ctx):
    
        def check(number):
            return number.content.isdigit()
    
        await ctx.send("Write 1:")
        
        
        try:   
            doneit = False
            messagecounter = 0
            duplicatelist = []
            uniquelist = []
            
            while(not doneit):
                message = await ctx.bot.wait_for(
                    "message", check=check, timeout=7.0                
                )
                if int(message.content) == 1:
                    messagecounter += 1
                    duplicatelist.append(message.author.id)
                    if message.author.id not in uniquelist:
                        uniquelist.append(message.author.id) 
                    
                    
                if messagecounter == 3:
                    doneit = True
                    
            await ctx.send("GJ BRO! \n {} \n {}".format(uniquelist, duplicatelist))
            
            
        except asyncio.TimeoutError:
             await ctx.send("Skriv 1 3 ganger:")
     