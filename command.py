import logging
import argparse
import shlex
import random
import json
import time
import os
import requests

import miraicle

from connect import reply_plain_text, reply_image
import dice

class commandParser(argparse.ArgumentParser):
    """Custom ArgumentPaarser that overrides _print_message"""

    def _print_message(self, message, file = None):
        if message:
            return message

class commandManager():
    def __init__(self, command_prefix = '.') -> None:
        self.command_prefix = command_prefix
        self.command_dict = {}
        self.command_alias_dict = {}
        
    def register_command(self, command_object, command_function):
        # register the command to a dict
        # TO-DO: Check illegal and duplicate names
        
        logging.info(f"Registering command [{command_object.name}]")
        self.command_dict[command_object.name] = (command_function, command_object)
        if command_object.aliases:
            for alias in command_object.aliases:
                logging.info(f"Registering command alias [{alias}] for command [{command_object.name}]")
                self.command_alias_dict[alias] = command_object.name
        

    def parse_command_from_msg(self, msg: miraicle.Message):
        try:
            args = shlex.split(msg.plain)
            if args and args[0][0] == self.command_prefix:
                if args[0][1:] in self.command_dict.keys():
                    return args[0][1:]
                elif args[0][1:] in self.command_alias_dict.keys():
                    return args[0][1:]
                
            return None
        except Exception:
            return None

    def is_registered_command(self, command: str):
        command_signature = command.replace(self.command_prefix, '')
        
        if command_signature in self.command_dict.keys(): return True
        else: return False
        
    def is_command_alias(self, alias: str):
        command_signature = alias.replace(self.command_prefix, '')
        
        if command_signature in self.command_alias_dict.keys(): return True
        else: return False
        
    def get_command_struct(self, command: str):
        command_signature = command.replace(self.command_prefix, '')

        if self.is_registered_command(command_signature):
            return self.command_dict[command_signature]
        if self.is_command_alias(command_signature):
            return self.command_dict[self.command_alias_dict[command_signature]]
        else: return None
        
    def get_command_function(self, command: str):
        return self.get_command_struct(command)[0]
    
    def run_command(self, msg: miraicle.Message):
        
        if isinstance(msg, miraicle.GroupMessage): 
            access_check_type = "GROUP"
            access_check_id = msg.group
        else: 
            access_check_type = "USER"
            access_check_id = msg.sender
        
        try:
            command = self.parse_command_from_msg(msg)
            if command:
                if self.is_command_alias(command):
                    logging.info(f"Resolved command alias [{command}] to command [{self.command_alias_dict[command]}] and running")
                else:
                    logging.info(f"Running command [{command}]")
                    
                command_struct = self.get_command_struct(command)
                command_obj = command_struct[1]
                if command_obj.access_check(id = access_check_id, mode = access_check_type):
                    command_function = self.get_command_function(command)
                    return command_function(msg)
                else:
                    logging.info("Command execution aborted: access rule violation")
        except Exception:
                logging.warning(f"Error running command {command}. Traceback:", exc_info=True)
        
    
command_manager = commandManager()

class command():
    
    def __init__(self, command_name: str, aliases: list = None, help_short = "", access_mode = "BLACK_LIST", 
                 default_group_blacklist = [], default_group_whitelist = [],
                 default_user_blacklist = [], default_user_whitelist = []) -> None:
        global command_manager
        
        self.command_manager = command_manager
        self.name = command_name
        self.aliases = aliases
        self.decorated = False
        self.help = help_short
        if access_mode in ["BLACK_LIST", "WHITE_LIST"]:
            self.access_mode = access_mode
        else:
            logging.warning(f"Unrecognized value {access_mode} of parameter access_mode for command {self.name}. Defaulting to BLACK_LIST mode.")
            self.access_mode = "BLACK_LIST"

        self.group_white_list = default_group_whitelist
        self.user_white_list = default_user_whitelist
        
        self.group_black_list = default_group_blacklist
        self.user_black_list = default_user_blacklist
        
        if self.access_mode == "BLACK_LIST" and (self.user_white_list or self.group_white_list):
            logging.warning(f"Command {self.name} access mode is BLACK_LIST but whitelists are given.")
            
        if self.access_mode == "WHITE_LIST" and (self.user_black_list or self.group_black_list):
            logging.warning(f"Command {self.name} access mode is WHITE_LIST but blacklists are given.")
        
    def __call__(self, command_function):
        
        def wrapper(*args, **kwargs):
            return command_function(*args, **kwargs)

        if not self.decorated:
            self.command_manager.register_command(self, wrapper)
            wrapper.__doc__ = command_function.__doc__
            self.decorated = True
        else:
            raise Exception("Attempt to re-decorate a used command object found!")
        
    def access_check(self, id = None,  mode = "GROUP"):
        if self.access_mode == "BLACK_LIST":
            if mode == "GROUP":
                if id in self.group_black_list: return False
                else: return True
            elif mode == "USER":
                if id in self.user_black_list: return False
                else: return True
        elif self.access_mode == "WHITE_LIST":
            if mode == "GROUP":
                if id in self.group_white_list: return True
                else: return False
            elif mode == "USER":
                if id in self.user_white_list: return True
                else: return False
            
        
    def access_mode_toggle(self):
        if self.access_mode == "BLACK_LIST":
            self.access_mode = "WHITE_LIST"
            logging.info(f"Command {self.name} access mode set to WHITE_LIST")
        else:
            self.access_mode = "BLACK_LIST"
            logging.info(f"Command {self.name} access mode set to BLACK_LIST")
        

    
@command(command_name = "help", help_short = "显示指令列表")
def help(msg: miraicle.GroupMessage):
    parser = commandParser(add_help = False)
    parser.add_argument("targetCommand", nargs = "?", default = "help")

    
    try:
        args = shlex.split(msg.plain)
        args = parser.parse_args(args[1:])
    except SystemExit:
        reply_plain_text(msg, "指定查询的命令名有点问题...可能是你手癌了？还是你有参数没输完整？")
        return -1

    def get_help():
        help_string = "可用指令：\n\n"
        for c in command_manager.command_dict.keys():
            help_string += f"[ {command_manager.command_prefix}{c} ]\n{command_manager.command_dict[c][1].help}\n\n"
            
        reply_plain_text(msg, f"{help_string}")    
    
    if args.targetCommand:
        if args.targetCommand == "help":
            get_help()

        elif command_manager.is_registered_command(args.targetCommand):
            help_string = command_manager.get_command_struct(args.targetCommand)[0].__doc__
            command = str(args.targetCommand).replace(command_manager.command_prefix, '')
            
            if help_string is None:
                reply_plain_text(msg, f"{command_manager.command_prefix}{command}\n\n 该指令还没有详细文档。因为小毛龙是懒狗。")
            else:
                reply_plain_text(msg, f"{command_manager.command_prefix}{command}\n\n {help_string}")
            return 0
        elif command_manager.is_command_alias(args.targetCommand):
            help_string = command_manager.get_command_struct(args.targetCommand)[0].__doc__
            command = str(args.targetCommand).replace(command_manager.command_prefix, '')
            
            if help_string is None:
                reply_plain_text(msg, f"[{command_manager.command_prefix}{command}]是[{command_manager.command_prefix}{command_manager.command_alias_dict[args.targetCommand]}]的别称。\n\n 该指令还没有详细文档。因为小毛龙是懒狗。")
            else:
                reply_plain_text(msg, f"[{command_manager.command_prefix}{command}]是[{command_manager.command_prefix}{command_manager.command_alias_dict[args.targetCommand]}]的别称。\n\n {command_manager.get_command_struct(args.targetCommand)[0].__doc__}")
            return 0
    else:        
        get_help()
    
@command(command_name = "r", help_short = "骰子，不过听说也能当计算器", aliases = ["rd"])
def roll(msg: miraicle.GroupMessage):
    '''骰子/计算器工具
    d100: 100面骰
    2d100: 两个100面骰相加
    2d100s: 两个100面骰里较小的那个
    3d100s2: 三个100面骰里小的两个之和
    3d100l2: 三个100面骰里大的两个之和
    dp, db: CoC 7th惩罚骰、奖励骰
    3dp: 等价于dp+dp+dp

    可用运算符(含义同Python):
    +,-,*,/,%,//,**
    
    可用函数：
    exp,log,log10,sin,cos,abs,sqrt,ceil,floor,round,max,min
    
    可用常量：
    pi
    '''
    
    parser = commandParser(add_help = False)
    parser.add_argument("diceExpr", nargs = "?", default = "d100")
    parser.add_argument("-h", "--help", action = "store_true")
    parser.add_argument("-v", "--value", type = int)
    parser.add_argument("-n", "--name", type = str)

    
    try:
        args = shlex.split(msg.plain)
        args = parser.parse_args(args[1:])
    except SystemExit:
        reply_plain_text(msg, "输入的参数有点问题...可能是你手癌了？还是你有参数没输完整？")
        return -1
    
    if args.help:
        reply_plain_text(msg, f"\n{dice.__doc__}")
        return 0
    
    elif args.value:
        roll_result = dice.parse_and_eval_dice(args.diceExpr)
        if not args.name:
            messgage_out = "某个...你没跟我讲到底是啥玩意的检定结果：\n"
        else:
            messgage_out = f"对{args.name}的检定结果：\n\n"
            
        messgage_out += f"{''.join(roll_result[0])}\n\n"
        
        if roll_result[1] == 1: messgage_out += "检定结论：大成功！！！"
        elif roll_result[1] in range(96, 101): messgage_out += "检定结论：大失败！！"
        elif roll_result[1] in range(2, int(args.value / 5) + 1): messgage_out += "检定结论：极难成功！！"
        elif roll_result[1] in range(int(args.value / 5) + 1, int(args.value / 2) + 1): messgage_out += "检定结论：困难成功！"
        elif roll_result[1] in range(int(args.value / 2) + 1, int(args.value)): messgage_out += "检定结论：通过"
        elif roll_result[1] in range(int(args.value), 96): messgage_out += "检定结论：失败！"

        else: messgage_out += "检定结论：你好像卡出bug来了"
        
        reply_plain_text(msg, messgage_out)
        return 0
        
    else:        
        roll_result = dice.parse_and_eval_dice(args.diceExpr)
        reply_plain_text(msg, ''.join(roll_result[0]))
        return 0

@command(command_name = "ping")
def echo(msg: miraicle.Message):
    reply_plain_text(msg, f"pong")

@command(command_name = "echo", help_short = "人类的本质")
def echo(msg: miraicle.Message):
    reply_plain_text(msg, f"[[复读机启动]]\n{msg.plain}")


# @command(command_name = "jrrp", help_short = "没做完。主要是不知道评论怎么写。")
def jrrp(msg: miraicle.Message):

    try:
        with open('data/jrrp.json', 'w+', encoding='utf-8') as f:
            record = json.load(f)

        if record['date'] != time.strftime('%Y-%m-%d', time.localtime()):
            # the record file is stale and should be truncated
            f.truncate(0)
            record = {'date' : time.strftime('%Y-%m-%d', time.localtime()), 'records' : []}
    except FileNotFoundError:
        record = {'date' : time.strftime('%Y-%m-%d', time.localtime()), 'records' : {}}

    user_id = str(msg.sender)

    if user_id in record['records']:
        return record['records'][user_id]
    else:
        with open('./static/jrrp_comments.json', 'r', encoding='utf-8') as f:
            jrrp_comments_table = json.load(f)

        jrrp = random.randint(1, 100)
        if jrrp == 1:
            comment = random.choice(jrrp_comments_table['1'])
        elif 1 < jrrp <= 5:
            comment = random.choice(jrrp_comments_table['5'])
        elif 5 < jrrp <= 20:
            comment = random.choice(jrrp_comments_table['20'])
        elif 20 < jrrp <= 50:
            comment = random.choice(jrrp_comments_table['50'])
        elif 50 < jrrp <= 99:
            comment = random.choice(jrrp_comments_table['99'])
        else:
            comment = random.choice(jrrp_comments_table['100'])
            
        reply_plain_text(msg, add_mention = True)
    
@command(command_name = "导随模拟", aliases = ["导随"], help_short = "绝对不精确的导随模拟器")
def dsmn(msg: miraicle.GroupMessage):
    with open('static/inst_sim.json', 'r', encoding='utf-8') as f:
        scene = json.load(f)

    job = random.choice(scene['job'])
    level = random.choice(scene['level'])
    result = random.choice(scene['result'])
    special = None

    # if random.randint(1, 100) <= 10:
        # special = random.choice(scene['special_event']['job'][job])
        
    reply_plain_text(msg, f" 用{job}排了导随！\n进入了{level}。\n\n{result}\n\n珍爱生命，合理导随。不卑不亢，大慈大悲。", add_mention = True)

    if special:
        reply_plain_text(msg, f"哦，对了，顺便一提，{special}")
        
        
@command(command_name = "抽卡", aliases = ["重抽"], help_short = "抽取一张奥秘卡。技能出卡会变为抽到的奥秘卡技能。")
def dsmn(msg: miraicle.GroupMessage, record_dict = {}):
    cards_melee = ["太阳神之衡", "放浪神之箭", "战争神之枪"]
    cards_range = ["世界树之干", "河流神之瓶", "建筑神之塔"]
    cards_crown = ["王冠之领主", "王冠之贵妇"]
    cards_random = {
        "黑夜学派" : "啊哦 这个东西不见了",
        "神圣路" : "啊哦 这个东西吉田祭天了",
        "回天" : "请把这个东西还给受了伤的盘子们",
        "青眼白龙" : "收着吧，听说值很多钱呢。",
        "打击" : "费用1。造成6点伤害。建议赶紧找商店烧了。",
        "打击+" : "费用1。造成9点伤害。你还把这玩意升级了？",
        "黑山羊" : "该造物献祭时视为3血点。",
        "单走一个6" : "得得得得得得得得得得得得",
        "聚热晶簇" : "被调度时对全场我方单位造成500真实伤害和5秒晕眩，随后消失。",
        "九宫幻卡：魔石精" : "★ ↑2 →3 ↓4 ←4",
        "阿米娅" : "★★★★★ 中坚术师 远程位 输出",
        "卡卡" : "我的力量无人能及！",
        "COC七版规则空白卡" : "...快跑。",
        "吹雪" : "はじめまして、吹雪です。よろしくお願いいたします！",
        "梦想天生" : "完全无法碰触到灵梦。不透明的透明人状态。\n好像是灵梦的究极奥义吧，似乎只是灵梦闭上眼睛，弹幕追踪敌人的位置自动射出而已的样子。\n顺便一提，刚开始这根本不是什么符卡，不过我给它安上了一个符卡的名字，让灵梦使出来玩了一下。要不然的话根本没有任何胜算。\n只有这个是天生拥有此能力的灵梦才能使出的符卡。因此名字上也用了天生二字。"
    }
    
    comment_same_type = {
        1 : "",
        2 : "\n\n你抽到了和上一张同属性的卡。我想这就是占星吧。",
        3 : "\n\n你连续抽到了3张发给远程/近战的卡，干得漂亮！",
        4 : "\n\n这个占星在做什么啊演的吧<se.1><se.1><se.1>",
        5 : "\n\n我靠 五张一样的了 你是哪里人啊 火页的吧",
        6 : "\n\n正在咏唱 纯正火页 [======---]",
        7 : "\n\n如果你看到这条说明我已经不知道该说什么了 接下来大概也没有评论了 要不我给你颁个奖吧"
    }
    
    result = random.randint(1, 100)

    prob = {
        "special": 20,
        "crown": 10,
    }
        
    if result in range(1, prob["special"]):
        record_dict[msg.sender] = ["special", 1]
        card = random.choice(list(cards_random.keys()))
        status = f"呃，这是...\n...[ {card} ]？\n\n"
        comment = cards_random[card]
    elif result in range(prob["special"], prob["special"] + prob["crown"]):
        record_dict[msg.sender] = ["crown", 1]
        card = random.choice(cards_crown)
        status = f"附加了“{card}（抽卡）”效果。\n\n"
        comment = "抽卡技能抽出王冠卡？你是不是开了？"
    else:
        if result in range(prob["special"] + prob["crown"], 100):
            
            if result%2 == 0:
                if not msg.sender in record_dict.keys():
                    record_dict[msg.sender] = ["ranged", 1]
                else:
                    if record_dict[msg.sender][0] == "ranged":
                        record_dict[msg.sender][1] += 1
                    else:
                        record_dict[msg.sender] = ["ranged", 1]
                        
                card = random.choice(cards_range)
                status = f"附加了“{card}（抽卡）”效果。"
            else:
                if not msg.sender in record_dict.keys():
                    record_dict[msg.sender] = ["melee", 1]
                else:
                    if record_dict[msg.sender][0] == "melee":
                        record_dict[msg.sender][1] += 1
                    else:
                        record_dict[msg.sender] = ["melee", 1]
                
                
                card = random.choice(cards_melee)
                status = f"附加了“{card}（抽卡）”效果。"
        
        comment = ""
        if record_dict[msg.sender][1] <= 7:
            comment = comment_same_type[record_dict[msg.sender][1]]
            
    reply_plain_text(msg, f" {status}{comment}", use_quote = True, add_mention = True)
    
# @command(command_name = "宏", aliases = ["macro"], help_short = "")
def macro(msg: miraicle.GroupMessage):

    parser = commandParser(add_help = False)
    parser.add_argument("-a", "--add", action = "store_true")
    parser.add_argument("-e", "--edit", type = int)
    parser.add_argument("-d", "--delete", type = int)
    parser.add_argument("-t", "--title", type = str)

    
    try:
        args = shlex.split(msg.plain)
        args = parser.parse_args(args[1:])
    except SystemExit:
        reply_plain_text(msg, "输入的参数有点问题...可能是你手癌了？还是你有参数没输完整？")
        return -1

@command(command_name = "吃啥", help_short = "")
def dsmn(msg: miraicle.GroupMessage):
    images_path = "./static/images/food"
    image_selected = random.choice(os.listdir(images_path))
        
    reply_image(msg, message = "我去问了阿虎，他说可以吃这个！", image_path = f"{images_path}/{image_selected}", add_mention = True)

@command(command_name = "安利", help_short = "给其他人卖安利", access_mode = "WHITE_LIST", default_group_whitelist = [484597471])
def macro(msg: miraicle.GroupMessage):

    parser = commandParser(add_help = False)
    parser.add_argument("-a", "--add", action = "store_true")
    parser.add_argument("-l", "--link", type = int)
    parser.add_argument("-d", "--delete", type = int)

    
    try:
        args = shlex.split(msg.plain)
        args = parser.parse_args(args[1:])
    except SystemExit:
        reply_plain_text(msg, "输入的参数有点问题...可能是你手癌了？还是你有参数没输完整？")
        return -1

@command(command_name = "稿子", help_short = "")
def macro(msg: miraicle.GroupMessage):

    parser = commandParser(add_help = False)
    parser.add_argument("-a", "--add", action = "store_true")
    parser.add_argument("-l", "--link", type = int)
    parser.add_argument("-d", "--delete", type = int)

    
    try:
        args = shlex.split(msg.plain)
        args = parser.parse_args(args[1:])
    except SystemExit:
        reply_plain_text(msg, "输入的参数有点问题...可能是你手癌了？还是你有参数没输完整？")