import re
import json
import copy
from enum import Enum

from libs.singleton import Singleton


class CharacterManager(metaclass = Singleton):

    def __init__(self, save_dir: str = None):

        self.next_id = 0
        self.characters = {}
        self.user_mapping = {}
        self.save_file = save_dir

        try:
            with open(save_dir, "r") as f:
                pass
            self.load()
        except (FileNotFoundError, TypeError) as e:
            pass

    def __str__(self):
        return json.dumps(dict(
            next_id = self.next_id,
            characters = self.characters,
            user_mapping = self.user_mapping
        ))

    def load(self):
        with open(self.save_file, "r") as f:
            records = json.load(f)

        self.next_id = records["next_id"]
        self.user_mapping = records["user_mapping"]

        for i in records["characters"].keys():
            char = Character()
            char.load(records["characters"][i])
            self.characters[i] = char

    def add_character(self, character_name, user_id):
        new_char_id = self.next_id
        self.next_id += 1

        self.characters[new_char_id] = Character(character_name, new_char_id, user_id)
        self.user_mapping[user_id] = new_char_id

    def get_player_current_character(self, user_id):
        try:
            return self.characters[self.user_mapping[user_id]]
        except KeyError:
            return None

    def switch_character_by_id(self, user_id, character_id):
        if isinstance(character_id, int):
            self.user_mapping[user_id] = character_id
        else:
            raise TypeError

    def get_character_by_name(self, character_name):
        chars = []

        for c in self.characters:
            if self.characters[c].name == character_name:
                chars.append(self.characters[c])

        return chars

    def get_character_by_owner(self, user_id):
        chars = []

        for c in self.characters:
            if self.characters[c].owner_id == user_id:
                chars.append(self.characters[c])

        return chars

    def get_character_by_id(self, character_id):

        for c in self.characters:
            if self.characters[c].id == character_id:
                return self.characters[c]

        return None


class Character:
    property_aliases = {
        "力量": ["str", "STR"],
        "敏捷": ["dex", "DEX"],
        "意志": ["pow", "POW"],
        "体质": ["con", "CON"],
        "外貌": ["app", "APP"],
        "教育": ["edu", "EDU", "知识"],
        "体型": ["siz", "SIZ"],
        "灵感": ["int", "INT", "智力"],
        "幸运": ["luk", "LUK", "运气"],
        "生命值": ["hp", "HP", "生命", "体力"],
        "理智值": ["san", "SAN", "san值", "理智"],
        "魔法值": ["mp", "MP", "魔法"],
        "移动力": ["mov", "MOV"],
        "克苏鲁神话": ["cm", "克苏鲁"],
        "信用评级": ["信用", "信誉"],
        "开锁": ["撬锁", "锁匠"],
        "汽车驾驶": ["汽车", "驾驶"],
        "导航": ["领航"],
        "计算机使用": ["计算机", "电脑"],
        "操作重型机械": ["重型操作", "重型机械", "重型"],
        "图书馆使用": ["图书馆"]
    }

    def __init__(self, name = "", character_id = 0, owner_id = 0, savefile = None):
        self.name = name
        self.id = character_id
        self.owner_id = owner_id
        self.properties = {
            "attributes": {
                "力量": None,
                "敏捷": None,
                "意志": None,
                "体质": None,
                "外貌": None,
                "教育": None,
                "体型": None,
                "灵感": None,
                "幸运": None,
            },
            "status": {
                "生命值": None,
                "理智值": None,
                "魔法值": None
                # "体格": None,
                # "移动力": None,
            },
            "skills": {
                "克苏鲁神话": None
            }
        }
        self.savefile = savefile

    def __str__(self):
        return json.dumps(dict(
            name = self.name,
            id = self.id,
            owner_id = self.owner_id,
            properties = self.properties,
        ))

    def save(self):
        pass

    def load(self, record_json: str):
        pass

    @classmethod
    def match_property_name(cls, property_name) -> str:
        for n in Character.property_aliases:
            if property_name in Character.property_aliases[n]:
                return n

        return property_name

    def property_exists(self, property_name: str) -> bool:
        if self.get(property_name) is None:
            return False
        else:
            if self.get(property_name) == -1:
                return False

        return True

    def get(self, property_name: str) -> int | None:
        property_name = self.match_property_name(property_name)

        if property_name in self.properties["attributes"].keys():
            if self.properties["attributes"][property_name] is None:
                return -1
            else:
                return self.properties["attributes"][property_name]
        elif property_name in self.properties["status"].keys():
            if self.properties["status"][property_name] is None:
                return -1
            else:
                return self.properties["status"][property_name]
        elif property_name in self.properties["skills"].keys():
            if self.properties["skills"][property_name] is None:
                return -1
            else:
                return self.properties["skills"][property_name]
        else:
            return None

    def set(self, property_name: str, set_value: int):
        property_name = self.match_property_name(property_name)

        if property_name in self.properties["attributes"].keys():
            self.properties["attributes"][property_name] = set_value
        elif property_name in self.properties["status"].keys():
            self.properties["status"][property_name] = set_value
        else:
            self.properties["skills"][property_name] = set_value

        self.save()

    def update(self, property_name: str, offset: int):
        property_name = self.match_property_name(property_name)
        self.set(property_name,
                 max(self.get(property_name) + offset, 0)
                 )

        self.save()

    def set_from_string(self, properties: str) -> dict:
        property_re = "\D+[0-9]+"
        property_update_re = "\D+(\+|-)[0-9]+"

        result = {
            "created": {},
            "updated": {},
            "failed": [],
            "warnings": {}
        }

        def property_check(p: str) -> bool:
            if self.get(p) >= 100:
                result["warnings"][p] = (f"属性值超过了99  ({self.get(p)})")
                return False
            elif self.get(p) == 0:
                result["warnings"][p] = (f"属性值为0")
                return False
            elif self.get(p) < 0:
                result["warnings"][p] = (f"必要的属性值未设置")
                return False

            return True

        while True:
            property_update_re_match = re.search(property_update_re, properties)
            property_re_match = re.search(property_re, properties)

            try:
                if property_update_re_match or property_re_match:
                    if property_update_re_match:
                        matched = property_re_match.group()
                        properties = properties.replace(matched, "", 1)
                        property_name = self.match_property_name(re.search("\D+", matched).group()[:-1])
                        property_exists = self.property_exists(property_name)
                        property_value_old = self.get(property_name)

                        property_modifier= int(re.search("(\+|-)[0-9]+", matched).group())
                        self.update(property_name, property_modifier)
                    elif property_re_match:
                        matched = property_re_match.group()
                        properties = properties.replace(matched, "", 1)
                        property_name = self.match_property_name(re.search("\D+", matched).group())
                        property_exists = self.property_exists(property_name)
                        property_value_old = self.get(property_name)

                        property_value = int(re.search("[0-9]+", matched).group())
                        self.set(property_name, property_value)

                    if property_exists:
                        result["updated"][property_name] = (property_value_old, self.get(property_name))
                    else:
                        result["created"][property_name] = self.get(property_name)

                    property_check(property_name)
                else:
                    if properties == "":
                        # all property successfully matched
                        break
                    else:
                        # remaining parts cannot be interpreted as a valid prop-set expr
                        result["failed"].append(properties)
                        break
            except Exception as e:
                result["failed"].append(matched)

        # check
        if self.get("SAN") > self.get("POW") - self.get("cm"):
            result["warnings"].append("当前的理智值超过了这张卡的上限")

        return result

    def get_attributes_value_sum(self):
        sum = 0

        for a in self.properties["attributes"]:
            if self.get(a) != -1:
                sum += self.get(a)

        if self.property_exists("幸运"):
            luk = self.get("幸运")
            sum -= luk
            return (sum, luk)
        else:
            return (sum, 0)


character_manager = CharacterManager("./data/coc/cm.json")