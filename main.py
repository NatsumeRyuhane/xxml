import logging
import time
from libs.custom_logging import *
from datetime import datetime

import threading
import signal
import os

time_start = datetime.now()
log_filename = f"{time_start.year}-{str(time_start.month).zfill(2)}-{str(time_start.day).zfill(2)}_{str(time_start.hour).zfill(2)}_{str(time_start.minute).zfill(2)}_{str(time_start.second).zfill(2)}"

os.makedirs("./logs/", exist_ok = True)

with open(f"./logs/{log_filename}.log", 'w', encoding = 'utf-8') as f:
    f.truncate(0)

logging.basicConfig(level = 'INFO', format = '[%(asctime)s] [%(thread)d - %(threadName)s] [%(levelname)s] %(message)s', encoding = 'utf-8',
                    handlers = [
                        logging.FileHandler(f"./logs/{log_filename}.log", encoding = 'utf-8'),
                        logging.StreamHandler()
                    ])

from commands.command import command_manager

from bots.mirai import Mirai, AsyncMirai
from bots.kook import KOOK

active_bots = [AsyncMirai, KOOK]
threads = []

def on_sigint(*args, **kwargs):
    for ab in active_bots:
        ab.shutdown()

# register signal handler
signal.signal(signal.SIGINT, on_sigint)

for ab in active_bots:
    t = threading.Thread(target = ab.run, name = ab.__class__.__name__)
    t.start()
    threads.append(t)

for t in threads:
    t.join()