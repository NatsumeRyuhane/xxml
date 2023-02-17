import logging
import time
import json
import traceback

# [ IMPORTANT ] Do not import ANYTHING except python built-in libs before
# overrides logging-config in mirai
time_start = int(time.time())
with open(f"./logs/bot_{time_start}.log", 'w', encoding='utf-8') as f:
    f.truncate(0)

logging.basicConfig(level = 'DEBUG', format = '[%(asctime)s] [%(levelname)s] %(message)s', encoding = 'utf-8',
                    handlers=[
                        logging.FileHandler(f"./logs/bot_{time_start}.log", encoding='utf-8'),
                        logging.StreamHandler()
                        ])

import miraicle

import command
from connect import bot
from bot_utils import chatlog_transcript
from auto_responders import auto_echo, anti_milk_trigger

config = {
    "command_blacklist" : {
        "group": []
    }
}


@miraicle.AsyncMirai.receiver('GroupMessage')
async def group_messages_recv(bot: miraicle.Mirai, msg: miraicle.GroupMessage):   
    try:
        await chatlog_transcript(msg)
        
        if command.command_manager.parse_command_from_msg(msg):
            logging.debug(f"Command matched in message [{msg.id}] from [{msg.sender}], plain = \"{msg.plain}\"")
            await command.command_manager.run_command(msg)
        else:
            await auto_echo(msg)
            await anti_milk_trigger(msg)
            
    except Exception as e:
        logging.error(f"Uncaught Exception rasied.\n", exc_info = True)
        
@miraicle.AsyncMirai.receiver('FriendMessage')
async def private_messages_recv(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    try:
        await chatlog_transcript(msg)
        
        if command.command_manager.parse_command_from_msg(msg):
            logging.debug(f"Command matched in message [{msg.id}] from [{msg.sender}], plain = \"{msg.plain}\"")
            await command.command_manager.run_command(msg)
        pass
    except Exception as e:
        logging.error(f"Uncaught Exception rasied.\n", exc_info = True)
        
@miraicle.AsyncMirai.receiver('TempMessage')
async def temp_messages_recv(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    try:
        await chatlog_transcript(msg)
        
        if command.command_manager.parse_command_from_msg(msg):
            logging.debug(f"Command matched in message [{msg.id}] from [{msg.sender}], plain = \"{msg.plain}\"")
            await command.command_manager.run_command(msg)
        pass
    except Exception as e:
        logging.error(f"Uncaught Exception rasied.\n", exc_info = True)

        
logging.info("Initialization Complete")
bot.run()