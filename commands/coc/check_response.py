from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
import khl

import shlex
import random

import commands.coc.character as character
from commands.coc.character import character_manager as cm
from commands.coc.check import SuccessLevel
import commands.coc.check as check

def construct_check_response(bot: Bot, msg: Message, result: check.Check) -> list[MessageComponent]:
    if cm.get_player_current_character(msg.context.sender_id) is None:
        name = msg.context.sender_name
    else:
        name = cm.get_player_current_character(msg.context.sender_id).name

    prompts = [
        f"一眼定真，{name}对{result.property_name}的检定为：",
        f"卜问天地通万灵，寻求我去路；\n{name}的{result.property_name}正在接受来自荒原的考验...",
        f"@全体成员 快来看！\n{name}又要用他无敌的{result.property_name}出来丢人了！",
        f"{name}坚定了自身信念，{result.property_name}检定的通过率上升了...吗?",
        f"「{result.property_name}」是个好东西，而{name}突然觉得，他上他也行",
    ]

    success_level_dict = {
        SuccessLevel.CRIT_FAILURE: {
            "level": "大失败!",
            "color": "#d54941",
            "comments": [
                "<se.6><se.6><se.6>",
                "\"想笑就笑吧\"",
                "⊂彡☆))∀`)"
            ],
            "image": Image(filepath = "./resources/images/xml/04.png")
        },
        SuccessLevel.FAILURE: {
            "level": "失败...",
            "color": "#ff9285",
            "comments": [
                "理论上说这里应该放一些批话，但是小毛龙写批话的尝试失败了。\n就像你的这个检定一样。",
                "这下有戏看了？"
            ],
            "image": None
        },
        SuccessLevel.SUCCESS: {
            "level": "成功",
            "color": "#e3f9e9",
            "comments": [
                "理论上说这里应该放一些批话，但是显然小毛龙还没有想好应该说什么",
                "ᕕ( ᐛ )ᕗ 也就那样吧？",
                "哦，你检定过了，但是我代表kp问你一句你确定要这么干么？"
            ],
            "image": None
        },
        SuccessLevel.DIFFICULT_SUCCESS: {
            "level": "困难成功！",
            "color": "#92dab2",
            "comments": [
                "理论上说这里应该放一些批话，但是显然小毛龙还没有想好应该说什么。\n困难成功的检定很难成功，所以它们对应的批话也很难想。",
                "直击！"
            ],
            "image": None
        },
        SuccessLevel.LIMITAL_SUCCESS: {
            "level": "极限成功!!",
            "color": "#56c08d",
            "comments": [
                "理论上说这里应该放一些批话，但是显然小毛龙还没有想好应该说什么。\n极限成功的检定非常难成功，所以它们对应的批话也很非常难想。",
                "暴击！"
            ],
            "image": None
        },
        SuccessLevel.CRIT_SUCCESS: {
        "level": "大成功!!!",
        "color": "#2ba471",
        "comments": [
            "感觉...不如原神...爆率...",
            "你走运了。不过也许其他的一些人要倒大霉了。",
            "获得启示：你以为这是水月肉鸽？",
            "( ﾟ∀。)?  耶？",
            "直击加暴击！!"
        ],
        "image": None
        }
    }
    if isinstance(bot, MiraiBot):
        response = [
            Text(f"检定结论：{success_level_dict[result.result_level]['level']}\n"),
            Text(f"{random.choice(success_level_dict[result.result_level]['comments'])}\n"),
        ]

        if success_level_dict[result.result_level]['image']:
            response.append(Image(filepath = success_level_dict[result.result_level]['image']))

        response.append(Text("\n"))

        if result.property_value_modifier.get_value() == 0:
            response.append(Text(f"详情:\n{name}的「{result.property_name}」技能：{result.property_value} \n\n{result.outcome} / {result.property_value}"))
        else:
            response.append(Text(f"详情:\n{name}的「{result.property_name}」技能：{result.property_value} ({result.property_value_modifier})\n\n{result.outcome} / {result.property_value + result.property_value_modifier.get_value()}"))

        return response
    else:
        response = khl.card.Card()

        response.append(khl.card.Module.Header(random.choice(prompts)))
        response.append(khl.card.Module.Section(khl.card.Element.Text(f"检定结论：{success_level_dict[result.result_level]}")))
        response.append(khl.card.Module.Context(f"*{random.choice(success_level_dict[result.result_level]['comments'])}*"))
        response.append(khl.card.Module.Divider())
        if result.property_value_modifier.get_value() == 0:
            response.append(khl.card.Module.Context(
                f"**详情:**\n{name}的「{result.property_name}」技能：{result.property_value} \n\n{result.outcome} / {result.property_value}"))
        else:
            response.append(khl.card.Module.Context(
                f"**详情:**\n{name}的「{result.property_name}」技能：{result.property_value} ({result.property_value_modifier})\n\n{result.outcome} / {result.property_value + result.property_value_modifier.get_value()}"))

        response.color = khl.card.Color(hex_color = random.choice(success_level_dict[result.result_level]['color']))

        return response