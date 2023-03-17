import logging
import miraicle
import random

from connect import bot

def auto_echo(msg: miraicle.GroupMessage, group_msg_cache = {}):
    if not msg.group in group_msg_cache.keys():
        if msg.plain != "":
            group_msg_cache[msg.group] = [msg.plain, 1]
    else:
        if msg.plain == group_msg_cache[msg.group][0]:
            group_msg_cache[msg.group][1] += 1
        else:
            group_msg_cache[msg.group] = [msg.plain, 1]
            
        if group_msg_cache[msg.group][1] == 3:
            logging.info(f"Auto-echo triggered in group {msg.group}")
            bot.send_group_msg(group = msg.group, msg = miraicle.Plain(group_msg_cache[msg.group][0]))