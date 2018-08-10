from .liveleaderboard import LiveLeaderboard

from redbot.core import commands
from redbot.core.data_manager import cog_data_path
import redbot.core

async def setup(bot: commands.Bot):
    cog = LiveLeaderboard(bot)
    bot.add_cog(cog)