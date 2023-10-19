from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
import khl

import shlex

import commands.coc.character as character
from commands.coc.character import character_manager as cm


@Command(command_name = "status", aliases = ["stats"], command_group = "coc")
async def status(bot: Bot, msg: Message):
    char: character.Character = cm.get_player_current_character(msg.context.sender_id)

    if char is None:
        if isinstance(bot, MiraiBot):
            await bot.reply_message(msg, f"{msg.context.sender_name}目前没有正在使用的角色卡")
        else:
            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"{msg.author.nickname}目前没有正在使用的角色卡"),
                        theme = khl.card.Types.Theme.WARNING
                    )
                )
            )
    else:
        attrs = ""
        if isinstance(bot, MiraiBot):
            for attr in char.properties["status"]:
                attrs += f"{attr} {char.get(attr)}    "

            await bot.reply_message(msg, f"「{cm.get_player_current_character(msg.context.sender_id).name}」的状态详情\n\n{attrs}")
        else:
            for attr in char.properties["status"]:
                attrs += f"{attr}  (font){char.get(attr)}(font)[primary]    "

            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"「{cm.get_player_current_character(msg.author_id).name}」的状态详情"),
                        khl.card.Module.Context(attrs),
                        theme = khl.card.Types.Theme.SUCCESS
                    )
                )
            )