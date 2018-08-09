
from .liveleaderboard import LiveLeaderboard

def setup(bot: commands.Bot):
    cog = OneWordStory(bot)
    bot.add_cog(cog)
    
 