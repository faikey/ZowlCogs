
from .leaderboard import leaderboard

def setup(bot):
    bot.add_cog(leaderboard(bot))