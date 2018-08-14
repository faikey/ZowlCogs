
from .leaderboard import Leaderboard

def setup(bot):
    bot.add_cog(Leaderboard(bot))