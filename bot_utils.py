import miraicle
import time
import os
import csv
import aiofiles

async def chatlog_transcript(msg: miraicle.Message):
    
    if not os.path.exists(f"./logs/chat_log/"):
            os.mkdir(f"./logs/chat_log/")
    
    if not os.path.exists(f"./logs/chat_log/group"):
        os.mkdir("./logs/chat_log/group")

    if isinstance(msg, miraicle.GroupMessage):
        
        if not os.path.exists(f"./logs/chat_log/group/{msg.group}"):
            os.mkdir(f"./logs/chat_log/group/{msg.group}")
            
        with open(f"./logs/chat_log/group/{msg.group}/group.chatlog.csv", "a+", encoding = "utf-8", newline = '') as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), msg.sender, msg.sender_name, msg.plain])
            
    elif isinstance(msg, miraicle.TempMessage):
        if not os.path.exists(f"./logs/chat_log/group/{msg.group}"):
            os.mkdir(f"./logs/chat_log/group/{msg.group}")
            
        with open(f"./logs/chat_log/group/{msg.group}/{msg.sender}.chatlog.csv", "a+", encoding = "utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), msg.sender, msg.sender_name, msg.plain])
                
    elif isinstance(msg, miraicle.FriendMessage):
        with open(f"./logs/chat_log/{msg.sender}.chatlog.csv", "a+", encoding = "utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), msg.sender, msg.sender_name, msg.plain])