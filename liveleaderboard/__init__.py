
from .liveleaderboard import LiveLeaderboard

def setup(bot: commands.Bot):
    cog = LiveLeaderBoard(bot)
    bot.add_cog(cog)
    
 