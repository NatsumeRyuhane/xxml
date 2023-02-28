import miraicle
from datetime import datetime
import random
from connect import *

@miraicle.scheduled_job(miraicle.Scheduler.every().hour.at("00:00:00"))
def water(bot: miraicle.Mirai):

    current = datetime.now()

    hr = current.hour

    hr_to_chi_dict = {
        0: "半夜十二点",
        1: "凌晨一点",
        2: "凌晨两点",
        3: "凌晨三点",
        4: "凌晨四点",
        5: "早上五点",
        6: "早上六点",
        7: "早上七点",
        8: "早上八点",
        9: "上午九点",
        10: "上午十点",
        11: "上午十一点",
        12: "中午十二点",
        13: "下午一点",
        14: "下午两点",
        15: "下午三点",
        16: "下午四点",
        17: "下午五点",
        18: "下午六点",
        19: "晚上七点",
        20: "晚上八点",
        21: "晚上九点",
        22: "晚上十点",
        23: "晚上十一点",
    }

    if hr in range(3, 7):
        pass

    elif hr == 2:
        msg_list = [
            "两点了，小小毛龙也要休息了。你为什么还没睡？",
            "比起喝水，我觉得差不多该去睡觉了...晚安！",
            "我知道也许你还不困，但这个点了，有什么事情还是明天再说吧。",
            "（你看见小小毛龙闭着眼趴在地上，发出了几声轻轻的咕噜声，大概是快睡着了。）"
        ]

        bot.send_group_msg(group = 484597471, 
                            msg = random.choice(msg_list))
    elif hr == 8:
        msg_list = [
            f"早上好！现在是{current.year}年{current.month}月{current.day}号的早上八点，天气你自己往窗外瞅吧，我不知道。"
            "早！不过现在这个点真的有人么？虽然是早上八点但是你们真的有人在吗？哈喽？",
            "小毛龙叫我早上八点的时候来群里吱一声。不过说实话我没太睡醒，现在是八点么？"
        ]            

        bot.send_group_msg(group = 484597471, 
                            msg = random.choice(msg_list))
    else:
        msg_list = [
            f"{hr_to_chi_dict[hr]}了。起来稍微活动下怎么样？",
            "又一个小时过去了。小小毛龙建议你少水会群，多喝点水。不如现在就去干个300ml。",
            "你知道吗？大多数医学指南推荐你每天摄入2000ml以上的水，以及0ml的无糖百事可乐。已经一个小时了，喝点水吧。可乐可以给我喝。",
            f"现在是{hr_to_chi_dict[hr]}整。我又来叫你们喝水了。回复TD也不能退订。",
            "又到整点了。你知道我是来教你干啥的。不过其实除了干水之外你也可以考虑做点别的，像是起来走走，可以防止血栓冒出来干你。",
            "乐观主义者说瓶子是半满的，悲观主义者说瓶子是半空的，而我只是想跟你讲又一个小时过去了，你能不能把这剩下半瓶水喝完？",
            "（小小毛龙打了个呵欠，然后在你面前晃了晃一个空着的水杯。）"
        ]            

        bot.send_group_msg(group = 484597471, 
                            msg = random.choice(msg_list))