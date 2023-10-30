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
from commands.coc.check_response import construct_check_response

import commands.coc.check as check


@Command(command_name = "rp", command_group = "coc")
async def rb(bot: Bot, msg: Message):
    parser = CommandParser(add_help = False)
    parser.add_argument("prop_name", nargs = "?", default = None)
    parser.add_argument("modifier_count", nargs = "?", default = None)

    prop_name = None
    modifier_count = 1

    try:
        args = shlex.split(msg.get_texts())
        args = parser.parse_args(args[1:])

        prop_name = args.prop_name
        if args.modifier_count:
            modifier_count = int(args.modifier_count)

        result = check.Check(char = cm.get_player_current_character(msg.context.sender_id),
                             property_name = prop_name,
                             dice_expression = f"1d100p{modifier_count}"
                             )

        if isinstance(bot, KOOKBot):
            await msg.reply(construct_check_response(bot, msg, result))
        else:
            await bot.reply_message(msg, construct_check_response(bot, msg, result))

    except (SystemExit, Exception) as e:
        if isinstance(bot, KOOKBot):
            response = khl.card.Card(
                khl.card.Module.Header(f"无法完成检定..."),
                theme = khl.card.Types.Theme.DANGER
            )

            if prop_name is None:
                response.append(khl.card.Module.Context(f"至少告诉我你要检定啥吧————"))
            elif cm.get_player_current_character(msg.author_id) is not None:
                response.append(khl.card.Module.Context(f"你的角色没有录入这项属性，因此无法使用此捷径指令"))
            elif cm.get_player_current_character(msg.author_id) is None:
                response.append(khl.card.Module.Context(f"你目前没有使用的的角色卡，因此无法使用此捷径指令"))
            else:
                response.append(khl.card.Module.Context(f"未知错误，你现在只能找小毛龙了..."))

            await msg.reply(khl.card.CardMessage(response))
        else:
            response = Message(msg.context.duplicate(), f"无法完成检定...")

            if prop_name is None:
                response.add_component(f"至少告诉我你要检定啥吧————")
            elif cm.get_player_current_character(msg.context.sender_id) is not None:
                response.add_component(f"你的角色没有录入这项属性，因此无法使用此捷径指令")
            elif cm.get_player_current_character(msg.context.sender_id) is None:
                response.add_component(f"你目前没有使用的的角色卡，因此无法使用此捷径指令")
            else:
                response.add_component(f"未知错误，你现在只能找小毛龙了...")

            await bot.reply_message(msg, response.components)