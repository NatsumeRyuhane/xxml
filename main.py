import logging
import time
import json
import traceback
import threading
from datetime import datetime

# [ IMPORTANT ] Do not import ANYTHING except python built-in libs before
# overrides logging-config in mirai
time_start = datetime.now()
log_filename = f"{time_start.year}-{str(time_start.month).zfill(2)}-{str(time_start.day).zfill(2)}_{str(time_start.hour).zfill(2)}_{str(time_start.minute).zfill(2)}_{str(time_start.second).zfill(2)}"

with open(f"./logs/bot_{log_filename}.log", 'w', encoding='utf-8') as f:
    f.truncate(0)

logging.basicConfig(level = 'INFO', format = '[%(asctime)s] [%(thread)d - %(threadName)s] [%(levelname)s] %(message)s', encoding = 'utf-8',
                    handlers=[
                        logging.FileHandler(f"./logs/bot_{log_filename}.log", encoding='utf-8'),
                        logging.StreamHandler()
                        ])

import miraicle

import command
from connect import bot
from bot_utils import *
from auto_responders import auto_echo
import scheduled_tasks

config = {
    "command_blacklist" : {
        "group": []
    }
}

@miraicle.Mirai.receiver('GroupMessage')
def group_messages_recv(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    def process():   
        try:
            chatlog_transcript(msg)
            
            if command.command_manager.parse_command_from_msg(msg):
                logging.debug(f"Command matched in message [{msg.id}] from [{msg.sender}], plain = \"{msg.plain}\"")
                command.command_manager.run_command(msg)
            else:
                auto_echo(msg)
                
        except Exception as e:
            logging.error(f"Uncaught Exception rasied.\n", exc_info = True)

    t = threading.Thread(target = process)
    t.start()

@miraicle.Mirai.receiver('FriendMessage')
def private_messages_recv(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    def process():
        try:
            chatlog_transcript(msg)
            
            if command.command_manager.parse_command_from_msg(msg):
                logging.debug(f"Command matched in message [{msg.id}] from [{msg.sender}], plain = \"{msg.plain}\"")
                command.command_manager.run_command(msg)
        except Exception as e:
            logging.error(f"Uncaught Exception rasied.\n", exc_info = True)

    t = threading.Thread(target = process)
    t.start()
        
@miraicle.Mirai.receiver('TempMessage')
def temp_messages_recv(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    def process():
        try:
            chatlog_transcript(msg)
            
            if command.command_manager.parse_command_from_msg(msg):
                logging.debug(f"Command matched in message [{msg.id}] from [{msg.sender}], plain = \"{msg.plain}\"")
                command.command_manager.run_command(msg)
        except Exception as e:
            logging.error(f"Uncaught Exception rasied.\n", exc_info = True)

    t = threading.Thread(target = process)
    t.start()

        
logging.info("Initialization Complete")
bot.run()