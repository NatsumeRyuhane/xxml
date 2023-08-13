import random

import discord
from discord.ext import commands

import libs.util as util

# nohup python3 -u bot_core.py > ./logs/sys.log 2
internal_ID = random.randint(100, 999)
client = commands.Bot(command_prefix = '.')
config = util.load_config_file('main.cfg')

def reload_config():
    global config
    config = util.load_config_file('main.cfg')