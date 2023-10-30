from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.kook import KOOKBot
import khl

import shlex

import commands.coc.character as character
from commands.coc.character import character_manager as cm
from commands.coc.check_response import construct_check_response

import commands.coc.check as check


@Command(command_name = "rc", aliases = ["ra"], command_group = "coc", help_short = "检定")
async def rc(bot: Bot, msg: Message):
    parser = CommandParser(add_help = False)
    parser.add_argument("prop_name", nargs = "?", default = None)
    parser.add_argument("prop_val", nargs = "?", default = None)

    prop_name = None
    prop_val = None

    try:
        args = shlex.split(msg.get_texts())
        args = parser.parse_args(args[1:])

        prop_name = args.prop_name
        if args.prop_val:
            prop_val = int(args.prop_val)

        if prop_val is None:
            result = check.Check(char = cm.get_player_current_character(msg.context.sender_id),
                                 property_name = prop_name
                                 )
        else:
            result = check.Check(property_name = prop_name,
                                 property_value = prop_val
                                 )

        await bot.reply_message(msg, construct_check_response(bot, msg, result))

    except (SystemExit, Exception) as e:
        if isinstance(bot, KOOKBot):
            response = khl.card.Card(
                khl.card.Module.Header(f"无法完成检定..."),
                theme = khl.card.Types.Theme.DANGER
            )

            if prop_name is None:
                response.append(khl.card.Module.Context(f"至少告诉我你要检定啥吧————"))
            elif (cm.get_player_current_character(msg.author_id) is not None) and (prop_val is None):
                response.append(khl.card.Module.Context(f"你的角色没有录入这项属性，请录入属性或带值检定"))
            elif (cm.get_player_current_character(msg.author_id) is None) and (prop_val is None):
                response.append(khl.card.Module.Context(f"你目前没有绑定的角色卡，请带值检定"))
            else:
                response.append(khl.card.Module.Context(f"未知错误，你现在只能找小毛龙了..."))

            await msg.reply(khl.card.CardMessage(response))
        else:
            message_out = [Text(f"无法完成检定...\n\n")]

            if prop_name is None:
                message_out.append(Text(f"至少告诉我你要检定啥吧————"))
            elif (cm.get_player_current_character(msg.context.sender_id) is not None) and (prop_val is None):
                message_out.append(Text(f"你的角色没有录入这项属性，请录入属性或带值检定"))
            elif (cm.get_player_current_character(msg.context.sender_id) is None) and (prop_val is None):
                message_out.append(Text(f"你目前没有绑定的角色卡，请带值检定"))
            else:
                message_out.append(Text(f"未知错误，你现在只能找小毛龙了..."))

            await bot.reply_message(msg, message_out)