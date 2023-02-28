import logging
import miraicle
import random

from connect import bot

def auto_echo(msg: miraicle.GroupMessage, group_msg_cache = {}):
    if not msg.group in group_msg_cache.keys():
        if msg.plain != "":
            group_msg_cache[msg.group] = [msg.plain, 1]
    else:
        if msg.plain == group_msg_cache[msg.group][0]:
            group_msg_cache[msg.group][1] += 1
        else:
            group_msg_cache[msg.group] = [msg.plain, 1]
            
        if group_msg_cache[msg.group][1] == 3:
            logging.info(f"Auto-echo triggered in group {msg.group}")
            bot.send_group_msg(group = msg.group, msg = miraicle.Plain(group_msg_cache[msg.group][0]))

def anti_milk_trigger(msg: miraicle.GroupMessage, group_msg_cache = {}):
    if msg.sender == 177249529:
        rspnd_dict = {
            "generic" : [
                "米尔克！你又在说骚话了！！",
                "你说这话你良心真的不会痛吗...",
                "......",
                "你知道小毛龙让我转录了聊天记录 其中也包括你米尔克的，永久保存，对吧？",
                "啊对的，对的对的对的，是的是的是的（无关心）",
                "我累了 你说啥是啥吧",
                "你说得对 但是原...总之揭开提什么什么的真相",
                "这要是在cfmy我现在就要让你 +崩破",
                "太逆天了 我都不知道该说什么",
                "米尔克 你是懂抽象的",
                "妈妈生的（即答",
                "好的雪豹我知道了 雪豹闭嘴",
                "复TD退订",
                ".bot off 米尔克",
                ".rc 让米尔克闭嘴\n\n 1d100 = 1\n检定结论：大成功！米尔克你闭嘴吧",
            ],
            "蓝色坏东西" : [
                "你这么说小心我咬你哦？（龇牙",
                "米尔克 本毛龙今天就要让你知道什么是真正的蓝色坏东西",
                "？欠扁是吧"
            ],
            "小毛龙" : [
                "关我屁事 老子只是一只小毛龙",
                "~给米尔克的生活小贴士~\n\n 1.神话传说一般认为猫猫有九条命\n2.现代科学一般认为，猫有超过九百种死因，包括被毛龙暴力谋杀",
                "老子要用绝峰箭扎你屁眼",
                "好的 正在为您查询 [牛奶肥橘的最佳油炸温度]... 结果显示是越高越好呢，炸糊了也没关系的 "
            ],
            "薄荷" : [
                "你说得对 今晚我就上你家把薄荷偷走",
                "真的吗 那薄荷给我尝尝（突然"
            ]
        }

        if random.randint(1, 100) <= 75:
            for key in rspnd_dict.keys():
                if key in msg.plain:
                    bot.send_group_msg(group = msg.group, msg = random.choice(rspnd_dict[key]))
                    return

            bot.send_group_msg(group = msg.group, msg = random.choice(rspnd_dict["generic"]))
        else:
            return