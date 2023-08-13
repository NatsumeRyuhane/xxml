from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
from bots.kook import KOOKBot
import bots.kook.khl as khl

import shlex

import commands.coc.character as character
from commands.coc.character import character_manager as cm


@Command(command_name = "new", aliases = ["new", "nc", "char"], command_group = "coc")
async def new(bot: Bot, msg: Message):
    try:
        args = shlex.split(msg.get_texts())
        char_name = args[1:][0]

        cm.add_character(char_name, msg.context.sender_id)

        if isinstance(bot, MiraiBot):
            await bot.reply_message(msg, f"你好，{char_name}。\n\n角色卡创建成功，已自动切换你使用的角色卡。\n接下来请使用 .st 导入角色属性。\n\n这张角色卡的ID为{cm.get_player_current_character(msg.context.sender_id).id}")
        elif isinstance(bot, KOOKBot):
            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"你好，{char_name}"),
                        khl.card.Module.Context(
                            f"角色卡创建成功，已自动切换你使用的角色卡。\n接下来请使用 .st 导入角色属性。\n\n这张角色卡的ID为{cm.get_player_current_character(msg.author_id).id}"),
                        theme = khl.card.Types.Theme.SUCCESS
                    )
                )
            )
    except IndexError:
        if isinstance(bot, MiraiBot):
            await bot.reply_message(msg, f"呃，你确定不告诉我你这卡叫啥名字吗？")
        elif isinstance(bot, KOOKBot):
            pass
