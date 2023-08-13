from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
from bots.kook import KOOKBot
import bots.kook.khl.card as khl

import shlex

from commands.coc.character import character_manager as cm


@Command(command_name = "r", aliases = ["rd"], command_group = "coc", help_short = "掷骰")
async def r(bot: Bot, msg: Message):
    parser = CommandParser(add_help = False)
    parser.add_argument("dice_expr", nargs = '*', default = ["1d100"])

    try:
        args = shlex.split(msg.get_texts())
        args = parser.parse_args(args[1:])

        if args.dice_expr:
            dice_expr = args.dice_expr[0]
            try:
                outcome = dice.DiceExpression(dice_expr)

                if isinstance(bot, MiraiBot):
                    await bot.reply_message(msg, content = [
                        Text(f"{msg.context.sender_name}扔出了{dice_expr}...\n"),
                        Text(f"结果：{outcome}"),
                    ])
                elif isinstance(bot, KOOKBot):
                    bot.reply_message(msg,
                        content = khl.card.CardMessage(
                            khl.card.Card(
                                khl.card.Module.Header(f"{msg.context.sender_name}扔出了..."),
                                khl.card.Module.Section(
                                    khl.card.Element.Text(f"{dice_expr} = {outcome.get_value()}"),
                                ),
                                khl.card.Module.Divider(),
                                khl.card.Module.Context(f"**详情:**\n{outcome}")
                            )
                        ),
                        use_quote = False
                    )
                else:
                    raise NotImplementedError
            except NotImplementedError or Exception:
                if isinstance(bot, MiraiBot):
                    await bot.reply_message(msg, f"小小毛龙看不太懂你说的{dice_expr}是什么意思。\n去找小毛龙的话他也许能看懂，但是他会揍你。")
                else:
                    await msg.reply(
                        khl.card.CardMessage(
                            khl.card.Card(
                                khl.card.Module.Header("骰子消失了..."),
                                khl.card.Module.Section(
                                    khl.card.Element.Text(
                                        f"小小毛龙看不太懂你说的{dice_expr}是什么意思。\n去找小毛龙的话他也许能看懂，但是他会揍你。"),
                                ),
                                theme = khl.card.Types.Theme.DANGER
                            )
                        )
                    )
    except (SystemExit, Exception) as e:
        await bot.reply_message(msg, Text("小毛龙没看懂你的指令怎么写的...？"))
        return -1
