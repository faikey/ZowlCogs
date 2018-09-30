from .events import Events

from redbot.core import commands, data_manager
from redbot.core.data_manager import cog_data_path
import redbot.core

async def setup(bot: commands.Bot):
    cog = Events(bot)
    #data_manager.load_bundled_data(cog, __file__)
    bot.add_cog(cog)
