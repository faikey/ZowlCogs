from pathlib import Path
from aiohttp import ClientSession
import shutil
import logging

from .events import Events

from redbot.core import commands
from redbot.core.data_manager import cog_data_path
import redbot.core

async def setup(bot: commands.Bot):
    cog = Events(bot)
        
    bot.add_cog(cog)