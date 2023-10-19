from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
from bots.kook import KOOKBot
import khl

import shlex

import commands.coc.character as character
from commands.coc.character import character_manager as cm


@Command(command_name = "list", aliases = ["sl"], command_group = "coc")
async def _list(bot: Bot, msg: Message):
    chars = cm.get_character_by_owner(msg.context.sender_id)

    if chars == []:
        if isinstance(bot, MiraiBot):
            await bot.reply_message(msg, f"{msg.context.sender_name}目前没有登记的角色卡")
        elif isinstance(bot, KOOKBot):
            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"{msg.author.nickname}目前没有登记的角色卡"),
                        theme = khl.card.Types.Theme.WARNING
                    )
                )
            )
    else:
        if cm.get_player_current_character(msg.context.sender_id) is None:
            prompt = f"以下是{msg.context.sender_name}登记的所有角色卡："
        else:
            prompt = f"{msg.context.sender_name}当前正在使用「{cm.get_player_current_character(msg.context.sender_id).name}」\n以下是{msg.context.sender_name}登记的所有角色卡："

        char_info = ""
        for c in chars:
            char_info += f"[{c.id}]  {c.name}\n"

        if isinstance(bot, MiraiBot):
            await bot.reply_message(msg, content = f"{prompt}\n\n{char_info}")
        elif isinstance(bot, KOOKBot):
            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(prompt),
                        khl.card.Module.Section(
                            khl.card.Element.Text(char_info),
                        ),
                        theme = khl.card.Types.Theme.SUCCESS
                    )
                )
            )
