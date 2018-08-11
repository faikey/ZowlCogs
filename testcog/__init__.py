from .testcog import TestCog

from redbot.core import commands
from redbot.core import data_manager
import redbot.core

async def setup(bot: commands.Bot):
    cog = TestCog(bot)
    data_manager.load_bundled_data(cog, __file__)
    bot.add_cog(cog)