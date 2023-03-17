import miraicle
import re
import sqlite3
from command import command

job_list = {
    "PLD": ["骑士", "剑盾小b"],
    "WAR": ["战士"],
    "DKN": ["暗黑骑士", "DK", "黑骑"],
    "GNB": ["绝枪战士", "绝枪"],
    "MNK": ["武僧", "芒克"],
    "DRG": ["龙骑士", "龙骑"],
    "NIN": ["忍者", "兔子"],
    "SAM": ["武士", "盘子", "萨姆来"],
    "RPR": ["钐镰客", "镰刀", "镰刀哥"],
    "BRD": ["吟游诗人", "诗人"],
    "MCH": ["机工士", "机工"],
    "DNC": ["舞者"],
    "BLM": ["黑魔法师", "黑魔", "黑膜"],
    "SMN": ["召唤师", "召唤", "召批"],
    "RDM": ["赤魔法师", "赤魔", "吃膜"],
    "WHM": ["白魔法师", "白魔", "白膜"],
    "SCH": ["学者", "小仙女"],
    "AST": ["占星术士", "占星"],
    "SGE": ["贤者", "高达"]
}

@command("武器需求", access_mode = "WHITE_LIST", default_group_whitelist = [675175346, 819684345])
def _(msg: miraicle.GroupMessage):
    message = msg.plain.split(" ")
    db = sqlite3.connect("./data/teamutils/demands.sqlite")
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `demands` (
            `id` INT UNSIGNED NOT NULL,
            `group_id` INT UNSIGNED NOT NULL,
            `WAR` INT NOT NULL DEFAULT 0,
            `DKN` INT NOT NULL DEFAULT 0,
            `GNB` INT NOT NULL DEFAULT 0,
            `MNK` INT NOT NULL DEFAULT 0,
            `DRG` INT NOT NULL DEFAULT 0,
            `NIN` INT NOT NULL DEFAULT 0,
            `SAM` INT NOT NULL DEFAULT 0,
            `RPR` INT NOT NULL DEFAULT 0,
            `BRD` INT NOT NULL DEFAULT 0,
            `MCH` INT NOT NULL DEFAULT 0,
            `DNC` INT NOT NULL DEFAULT 0,
            `BLM` INT NOT NULL DEFAULT 0,
            `SMN` INT NOT NULL DEFAULT 0,
            `RDM` INT NOT NULL DEFAULT 0,
            `WHM` INT NOT NULL DEFAULT 0,
            `SCH` INT NOT NULL DEFAULT 0,
            `AST` INT NOT NULL DEFAULT 0,
            `SGE` INT NOT NULL DEFAULT 0,
            PRIMARY KEY (id, group_id)
        );
    """)

    if message[1] == "set":
        msg_body = ''.join(message[2:])
        params = {}
        while msg_body:
            job = re.match("\D", string).group()
            msg_body.replace(job, "", 1)
            pts = re.match("\d", string).group()
            msg_body.replace(pts, "", 1)

        cursor.execute(f"SELECT `id` from `demands` WHERE `id`={message.sender}")
        if len(cursor) == 0:
            cursor.execute(f"INSERT INRO `demands` VALUES ({message.sender})")
        

