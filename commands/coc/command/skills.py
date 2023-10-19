from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
import khl

import shlex

import commands.coc.character as character
from commands.coc.character import character_manager as cm


@Command(command_name = "skills", aliases = ["skill"], command_group = "coc")
async def skills(bot: Bot, msg: Message):
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
        count = 0
        skills_sorted = sorted(char.properties["skills"].items(), key = lambda x: x[1], reverse = True)
        if isinstance(bot, MiraiBot):
            for skill in skills_sorted:
                attrs += f"{skill[0]} {char.get(skill[0])}    "
                count += 1

                if count == 3:
                    attrs += "\n"
                    count = 0

            await bot.reply_message(msg, f"「{cm.get_player_current_character(msg.context.sender_id).name}」的技能详情\n\n{attrs}")
        else:
            for skill in skills_sorted:
                attrs += f"{skill[0]}  (font){char.get(skill[0])}(font)[primary]    "
                count += 1

                if count == 4:
                    attrs += "\n"
                    count = 0

            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"「{cm.get_player_current_character(msg.author_id).name}」的技能详情"),
                        khl.card.Module.Context(attrs),
                        theme = khl.card.Types.Theme.SUCCESS
                    )
                )
            )
