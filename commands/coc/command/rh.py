import random

from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
import bots.kook.khl as khl

import shlex

from commands.coc.character import character_manager as cm


@Command(command_name = "rh", command_group = "coc")
async def rh(bot: Bot, msg: Message):
    parser = CommandParser(add_help = False)
    parser.add_argument("dice_expr", nargs = '*', default = ["1d100"])

    try:
        args = shlex.split(msg.get_texts())
        args = parser.parse_args(args[1:])

        if args.dice_expr:
            dice_expr = args.dice_expr[0]
            try:
                outcome = dice.DiceExpression(dice_expr)

                prompt_messages = [
                    f"{msg.context.sender_name}扔出了一个暗骰...",
                    f"豆豆叫我给{msg.context.sender_name}扔了个大失败！"
                ]

                if isinstance(bot, MiraiBot):
                    await bot.reply_message(msg, random.choice(prompt_messages))

                    result_msg_context = Context(context_type = Context.MessageContextType.PRIVATE, sender_id = msg.context.sender_id)

                    result_msg = Message(result_msg_context, components = [
                        Text("暗骰结果\n"),
                        Text(f"{dice_expr} = {outcome.get_value()}")
                    ])
                    await bot.send_message(result_msg)

                else:
                    await bot.reply_message(msg, KOOKCardMessage(
                            khl.card.CardMessage(
                                khl.card.Card(
                                    khl.card.Module.Header(random.choice(prompt_messages)),
                                    khl.card.Module.Context(f"但这到底意味着什么呢？")
                                )
                            )
                        )
                    )

                    result_msg_context = msg.context.duplicate()
                    result_msg_context.visibility = Context.Visibility.PRIVATE

                    result_msg = Message(result_msg_context, components = [
                        KOOKCardMessage(
                            khl.card.CardMessage(
                                khl.card.Card(
                                    khl.card.Module.Header("暗骰结果"),
                                    khl.card.Module.Section(
                                        khl.card.Element.Text(f"{dice_expr} = {outcome.get_value()}"),
                                    ),
                                    khl.card.Module.Divider(),
                                    khl.card.Module.Context(
                                        f"**详情:**\n{outcome}\n\n注意：暗骰的结果将不会保存在记录中，并会在下次刷新页面时消失")
                                )
                            )
                        )
                    ])

                    await bot.send_message(result_msg, use_qoute = False)

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
        pass
