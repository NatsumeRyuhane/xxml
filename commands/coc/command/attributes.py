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


@Command(command_name = "attributes", aliases = ["attr", "attrs"])
async def attr(bot: Bot, msg: Message):
    char: character.Character = cm.get_player_current_character(msg.context.sender_id)

    if char is None:
        if isinstance(bot, KOOKBot):
            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"{msg.context.sender_name}目前没有正在使用的角色卡"),
                        theme = khl.card.Types.Theme.WARNING
                    )
                )
            )
        else:
            await bot.reply_message(msg, f"{msg.context.sender_name}目前没有正在使用的角色卡")
    else:
        attrs = ""
        count = 0

        if isinstance(bot, KOOKBot):
            for attr in char.properties["attributes"]:
                attrs += f"{attr}  (font){char.get(attr)}(font)[primary]    "
                count += 1

                if count == 3:
                    attrs += "\n"
                    count = 0

            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"「{cm.get_player_current_character(msg.author_id).name}」的属性详情"),
                        khl.card.Module.Section(
                            khl.card.Element.Text(
                                f"属性合计：{sum(char.properties['attributes'].values()) - char.get('幸运')} + {char.get('幸运')}"),
                        ),
                        khl.card.Module.Divider(),
                        khl.card.Module.Context(attrs),
                        theme = khl.card.Types.Theme.SUCCESS
                    )
                )
            )
        else:
            for attr in char.properties["attributes"]:
                attrs += f"{attr} {char.get(attr)}    "
                count += 1

                if count == 2:
                    attrs += "\n"
                    count = 0

            await bot.reply_message(msg, f"「{cm.get_player_current_character(msg.context.sender_id).name}」的属性详情\n\n属性合计：{char.get_attributes_value_sum()[0]} + {char.get_attributes_value_sum()[1]}\n\n{attrs}")