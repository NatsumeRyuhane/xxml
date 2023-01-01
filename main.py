import logging
import time
import json

# [ IMPORTANT ] Do not import ANYTHING except python built-in libs before
# overrides logging-config in mirai
time_start = int(time.time())
with open(f"./logs/bot_{time_start}.log", 'w', encoding='utf-8') as f:
    f.truncate(0)
logging.basicConfig(filename = f"./logs/bot_{time_start}.log", level = 'DEBUG', format = '[%(asctime)s] [%(levelname)s] %(message)s', encoding = 'utf-8')

import miraicle

import command
from connect import bot
from bot_utils import chatlog_transcript
from auto_responders import auto_echo

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
            
    except Exception as e:
        logging.error(f"Uncaught Exception rasied. Traceback: {e}")
        
@miraicle.AsyncMirai.receiver('FriendMessage')
async def private_messages_recv(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    try:
        await chatlog_transcript(msg)
        
        if command.command_manager.parse_command_from_msg(msg):
            logging.debug(f"Command matched in message [{msg.id}] from [{msg.sender}], plain = \"{msg.plain}\"")
            await command.command_manager.run_command(msg)
        pass
    except Exception as e:
        logging.error(f"Uncaught Exception rasied. Traceback: {e}")
        
@miraicle.AsyncMirai.receiver('TempMessage')
async def temp_messages_recv(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    try:
        await chatlog_transcript(msg)
        
        if command.command_manager.parse_command_from_msg(msg):
            logging.debug(f"Command matched in message [{msg.id}] from [{msg.sender}], plain = \"{msg.plain}\"")
            await command.command_manager.run_command(msg)
        pass
    except Exception as e:
        logging.error(f"Uncaught Exception rasied. Traceback: {e}")

        
logging.info("Initialization Complete")
bot.run()