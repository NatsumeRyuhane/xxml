from commands.command import *
from libs.message import *
from libs.bot import Bot

import random
import os


@Command(command_name = "吃啥", short_help = "")
async def func(bot: Bot, msg: Message):
    images_path = "./resources/images/food"
    image_selected = random.choice(os.listdir(images_path))

    await bot.reply_message(msg, content = [
        Quote(msg.context.msg_id),
        At(msg.context.sender_id, msg.context.sender_name),
        Text(" 我去问了阿虎，他说可以吃这个！"),
        Image(filepath = f"{images_path}/{image_selected}")
    ])
