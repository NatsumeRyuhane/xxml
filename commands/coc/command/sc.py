from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
import khl

import shlex

import commands.coc.character as character
from commands.coc.character import character_manager as cm
from commands.coc.check import SuccessLevel

import commands.coc.check as check
import random


@Command(command_name = "sancheck", aliases = ["sc"], command_group = "coc")
async def sc(bot: Bot, msg: Message):
    parser = CommandParser(add_help = False)
    parser.add_argument("sc_exprs", nargs = '*')

    sc_exprs = None
    try:
        args = shlex.split(msg.get_texts())
        args = parser.parse_args(args[1:])

        if args.sc_exprs:
            sc_exprs = args.sc_exprs[0]

        sc_expr = sc_exprs.split('/')
        temp_insanity_dict = {
            "失忆": "你不知道你为何来到这里...你脑海中最后一刻的记忆停留在那个温馨的，安全的地方。",
            "假性残疾": "声音或是光影离你而去，抑或是肢体忽然失去知觉和动作，总之，你的一部分身体似乎抛弃了你。",
            "暴力倾向": "所有人都是敌人！你渴望撕碎敌人！",
            "偏执": "你感受到一股视线无时无刻不在监视着你...这一切都是「祂」的阴谋，而你所谓的同伴也正是「祂」派来的棋子...",
            "人际依赖": "这个世界的真相对你来说过分残酷了。但只要还有他...对，只要在他身边...无论如何都要前往他的身边...",
            "昏厥": "晚安，玛卡巴卡。",
            "逃避行为": "逃跑很可耻，但也很有用。最重要的是，你确实能溜得很快。",
            "歇斯底里": "情绪不断从你身体的各处涌出，但没人能理解你混乱的表情和动作在试图表达什么东西。",
            "恐惧": "随着世界像你展露出帷幕后方的些许光影，你才忽然意识到原来「那个东西」背后潜藏着的，对你的恶意和危险...",
            "躁狂": "你不再能忍受「那样东西」的存在。你一定要摆脱它！不顾一切的摆脱它！即使这意味着..."
        }

        char: character.Character = cm.get_player_current_character(msg.context.sender_id)
        if char is None:
            if isinstance(bot, MiraiBot):
                await bot.reply_message(msg, content = [
                    Text("无法完成检定...\n\n快速sancheck只能在使用角色卡的状态下进行"),

                ])
            else:
                await msg.reply(
                    khl.card.CardMessage(
                        khl.card.Card(
                            khl.card.Module.Header("无法完成检定..."),
                            khl.card.Module.Context("快速sancheck只能在使用角色卡的状态下进行"),
                            theme = khl.card.Types.Theme.DANGER
                        )
                    )
                )
                return
        else:
            try:
                precheck_san = char.get("SAN")
                result = check.Check(
                    char = char,
                    property_name = "SAN"
                )
                if result.result_level == SuccessLevel.CRIT_FAILURE:
                    san_damage = dice.DiceExpression(sc_expr[1])
                    san_damage_value = san_damage.get_max_value()
                    char.update("SAN", -1 * san_damage_value)
                elif result.result_level == SuccessLevel.FAILURE:
                    san_damage = dice.DiceExpression(sc_expr[1])
                    san_damage_value = san_damage.get_value()
                    char.update("SAN", -1 * san_damage_value)
                elif result.result_level == SuccessLevel.CRIT_SUCCESS:
                    san_damage = dice.DiceExpression(sc_expr[0])
                    san_damage_value = san_damage.get_min_value()
                    char.update("SAN", -1 * san_damage_value)
                else:
                    san_damage = dice.DiceExpression(sc_expr[0])
                    san_damage_value = san_damage.get_value()
                    char.update("SAN", -1 * san_damage_value)

                if isinstance(bot, MiraiBot):
                    response = [
                        Text(f"{char.name}的理智受到了冲击！\n\n"),
                        Text(f"理智 -{san_damage_value}  [{precheck_san} ➔ {char.get('SAN')}]\n\n")
                    ]
                else:
                    response = khl.card.Card(
                        khl.card.Module.Header(f"{char.name}的理智受到了冲击！"),
                        khl.card.Module.Section(
                            khl.card.Element.Text(
                                f"**理智**  (font)-{san_damage_value}(font)[secondary]\n  {precheck_san} ➔ (ins){char.get('SAN')}(ins)\n\n"),
                        ),
                        theme = khl.card.Types.Theme.WARNING
                    )

                if san_damage_value >= 5:
                    int_result = check.Check(
                        char = char,
                        property_name = "INT"
                    )
                    if int_result.result_level >= SuccessLevel.SUCCESS:
                        temp_insanity = random.choice(list(temp_insanity_dict.keys()))
                        duration = dice.DiceExpression('1d10')

                        if isinstance(bot, MiraiBot):
                            response.append(Text(f"深入灵魂的恐惧击碎了你的精神...\n获得临时恐惧: {temp_insanity}, 持续{duration.get_value()}轮\n\n"))
                            response.append(Text(f"{temp_insanity_dict[temp_insanity]}\n\n"))
                            response.append(Text(f"详情\n  [理智检定] 1d100 = {result.outcome_value} / {precheck_san}\n  [理智损失] {san_damage.raw_expr} = {san_damage_value}\n  [智力检定] 1d100 = {int_result.outcome_value} / {char.get('INT')}\n  [临时疯狂时长] 1d10 = {duration.get_value()}"))
                        else:
                            response.append(khl.card.Module.Divider())
                            response.append(khl.card.Module.Section(khl.card.Element.Text(
                                f"*深入灵魂的恐惧击碎了你的精神...*\n获得临时恐惧: **{temp_insanity}**, 持续**{duration.get_value()}**轮")))
                            response.append(khl.card.Module.Context(f"*{temp_insanity_dict[temp_insanity]}*"))

                            response.append(khl.card.Module.Divider())
                            response.append(khl.card.Module.Context(
                                f"**详情**\n  [理智检定] 1d100 = {result.outcome_value} / {precheck_san}\n  [理智损失] {san_damage.raw_expr} = {san_damage_value}\n  [智力检定] 1d100 = {int_result.outcome_value} / {char.get('INT')}\n  [临时疯狂时长] 1d10 = {duration.get_value()}"))
                            response.theme = khl.card.Types.Theme.DANGER
                    else:
                        if isinstance(bot, MiraiBot):
                            response.append(Text("你无法理解你所见证的巨大的恐怖背后隐藏着什么，但也许，这是一种幸运。\n\n"))
                            response.append(Text(f"详情\n  [理智检定] 1d100 = {result.outcome_value} / {precheck_san}\n  [理智损失] {san_damage.raw_expr} = {san_damage_value}\n  [智力检定] 1d100 = {int_result.outcome_value} / {char.get('INT')}"))
                        else:
                            response.append(khl.card.Module.Divider())
                            response.append(
                                khl.card.Module.Context("*你无法理解你所见证的巨大的恐怖背后隐藏着什么，但也许，这是一种幸运。*"))

                            response.append(khl.card.Module.Divider())
                            response.append(khl.card.Module.Context(
                                f"**详情**\n  [理智检定] 1d100 = {result.outcome_value} / {precheck_san}\n  [理智损失] {san_damage.raw_expr} = {san_damage_value}\n  [智力检定] 1d100 = {int_result.outcome_value} / {char.get('INT')}"))
                            response.theme = khl.card.Types.Theme.WARNING
                else:
                    if isinstance(bot, MiraiBot):
                        response.append(Text(f"详情\n  [理智检定] 1d100 = {result.outcome_value} / {precheck_san}\n  [理智损失] {san_damage.raw_expr} = {san_damage_value}"))
                    else:
                        response.append(khl.card.Module.Context(
                            f"**详情**\n  [理智检定] 1d100 = {result.outcome_value} / {precheck_san}\n  [理智损失] {san_damage.raw_expr} = {san_damage_value}"))
                        response.theme = khl.card.Types.Theme.SUCCESS

                await bot.reply_message(msg, response)
            except Exception as e:
                if isinstance(bot, MiraiBot):
                    await bot.reply_message(msg, content = [
                        Text("无法完成检定...\n\n请检查给定的sc表达式是否正确")
                    ])
                else:
                    await msg.reply(
                        khl.card.CardMessage(
                            khl.card.Card(
                                khl.card.Module.Header("无法完成检定..."),
                                khl.card.Module.Context("请检查给定的sc扣san表达式是否正确"),
                                theme = khl.card.Types.Theme.DANGER
                            )
                        )
                    )
    except SystemExit:
        pass
    except Exception as e:
        pass
