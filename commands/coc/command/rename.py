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


@Command(command_name = "rename", aliases = ["nn"], command_group = "coc")
async def rename(bot: Bot, msg: Message):
    try:
        args = shlex.split(msg.get_texts())
        new_name = args[1:][0]

        char: character.Character = cm.get_player_current_character(msg.context.sender_id)
        if char is None:
            if isinstance(bot, MiraiBot):
                await bot.reply_message(msg, "重命名失败。当前并没有正在使用的角色卡。")
            elif isinstance(bot, KOOKBot):
                await msg.reply(
                    khl.card.CardMessage(
                        khl.card.Card(
                            khl.card.Module.Header(f"重命名失败..."),
                            khl.card.Module.Context(f"当前并没有正在使用的角色卡"),
                            theme = khl.card.Types.Theme.DANGER
                        )
                    )
                )
                return

        prev_name = char.name
        char.name = new_name

        if isinstance(bot, MiraiBot):
            await bot.reply_message(msg, f"「{prev_name}」已重命名为「{char.name}」")
        elif isinstance(bot, KOOKBot):
            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"「{prev_name}」已重命名为「{char.name}」"),
                        theme = khl.card.Types.Theme.SUCCESS
                    )
                )
            )
    except IndexError:
        pass
