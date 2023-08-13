from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
import bots.kook.khl as khl

import shlex

import commands.coc.character as character
from commands.coc.character import character_manager as cm


@Command(command_name = "show", command_group = "coc")
async def show(bot: Bot, msg: Message):
    char: character.Character = cm.get_player_current_character(msg.context.sender_id)

    if char is None:
        if isinstance(bot, MiraiBot):
            await bot.reply_message(msg, f"{msg.context.sender_name}目前没有正在使用的角色卡")
        else:
            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"{msg.context.sender_name}目前没有正在使用的角色卡"),
                        theme = khl.card.Types.Theme.WARNING
                    )
                )
            )
    else:
        args = shlex.split(msg.get_texts())

        property_name = char.match_property_name(args[1:][0])
        property_val = char.get(property_name)

        if property_val is None:
            if isinstance(bot, MiraiBot):
                await bot.reply_message(msg, f"「{cm.get_player_current_character(msg.context.sender_id).name}」未设置「{property_name}」属性")
            else:
                await msg.reply(
                    khl.card.CardMessage(
                        khl.card.Card(
                            khl.card.Module.Header(
                                f"「{cm.get_player_current_character(msg.author_id).name}」未设置「{property_name}」属性"),
                            theme = khl.card.Types.Theme.WARNING
                        )
                    )
                )
        else:
            if isinstance(bot, MiraiBot):
                await bot.reply_message(msg, f"「{cm.get_player_current_character(msg.context.sender_id).name}」的「{property_name}」属性为{property_val}")
            else:
                await msg.reply(
                    khl.card.CardMessage(
                        khl.card.Card(
                            khl.card.Module.Header(
                                f"「{cm.get_player_current_character(msg.author_id).name}」的「{property_name}」属性为{property_val}"),
                            theme = khl.card.Types.Theme.SUCCESS
                        )
                    )
                )
