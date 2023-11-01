from commands.command import *
from libs.message import *
from libs.bot import Bot

@Command(command_name = "ping", short_help = "pong")
async def ping(bot: Bot, msg: Message):

    await bot.reply_message(msg, [
        Quote(msg.context.msg_id),
        Text("pong")
    ])