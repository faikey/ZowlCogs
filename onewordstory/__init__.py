
from .onewordstory import OneWordStory
from redbot.core import commands
from redbot.core.data_manager import cog_data_path
import redbot.core

def setup(bot: commands.Bot):
    cog = OneWordStory(bot)
    bot.add_cog(cog)
    
 