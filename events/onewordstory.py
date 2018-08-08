
# Red
from redbot.core import Config, bank, commands, checks
from redbot.core.data_manager import bundled_data_path

# Standard Library
import asyncio
import csv
import logging
import random
import textwrap
import uuid
from bisect import bisect
from copy import deepcopy
from itertools import zip_longest

# BOSSFIGHTS
import io
import aiohttp
import datetime


# Discord.py
import discord

# Red
from redbot.core import Config, bank, commands
from redbot.core.data_manager import bundled_data_path

        
class BossFights: