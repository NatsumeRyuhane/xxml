import random
from math import *
import re


def restricted_eval(expr: str):

    allowed_names_list = [

    ]

    allowed_names = dict([(name, globals().get(name, None)) for name in allowed_names_list])

    return eval(expr,
                # __globals
                { "__builtins__": None },
                # __locals
                allowed_names)

class Dice:

    def __init__(self, count: int, face: int, bonus = None, penalty = None, name = "", expr = ""):
        self.name = name
        self.expr = expr
        self.count = count
        self.face = face
        self.bonus = bonus
        self.penalty = penalty

        if self.count == 1:
            if bonus and penalty:
                raise NotImplementedError("bonus and penalty dice cannot be applied together")

        elif bonus or penalty:
            raise NotImplementedError("cannot apply bonus/penalty dice to multiple dices")

        self.value = None
        self.roll_records = {
            "roll": [],
            "bonus": [],
            "penalty": []
            }

        for i in range(0, self.count):
            self.roll_records["roll"].append(random.randint(1, self.face))

        if self.bonus:
            for i in range(0, self.bonus):
                self.roll_records["bonus"].append(random.randint(1, max(floor(self.face / 10), 1)))

        if self.penalty:
            for i in range(0, self.penalty):
                self.roll_records["penalty"].append(random.randint(1, max(floor(self.face / 10), 1)))

        self.get_value()

    def get_value(self):
        if self.value:
            return self.value
        else:
            if self.count > 1:
                self.value = sum(self.roll_records["roll"])
            else:
                if self.bonus:
                    self.value = min(self.roll_records["roll"][0], min(self.roll_records["bonus"]) * 10 + self.roll_records["roll"][0] % 10)
                elif self.penalty:
                    self.value = max(self.roll_records["roll"][0], max(self.roll_records["penalty"]) * 10 + self.roll_records["roll"][0] % 10)
                else:
                    self.value = sum(self.roll_records["roll"])

            return self.value

    def get_max_value(self):
        if self.value:
            return self.value
        else:
            if self.count > 1:
                return self.count * self.face
            else:
                return self.face

    def get_min_value(self):
        if self.value:
            return self.value
        else:
            if self.count > 1:
                return self.count
            else:
                return 1

    def get_roll_detail(self):
        string = f"{self.count}d{self.face} = {self.roll_records['roll']}"
        if self.bonus:
            string += f"\n奖励骰：{self.roll_records['bonus']}\n\n结果 = {self.value}"
        elif self.penalty:
            string += f"\n惩罚骰：{self.roll_records['penalty']}\n\n结果 = {self.value}"

        return string


class DiceExpression:

    def __init__(self, expr: str):
        dice_re = "([1-9]\d*)?[dD]([1-9]\d*)+((([bB]([1-9]\d*)?))|(([pP]([1-9]\d*)?)))?"
        self.raw_expr = expr.replace(" ", "")
        self.parsed_expr = self.raw_expr
        self.dice_list = []

        while True:
            re_match = re.search(dice_re, self.parsed_expr)
            if re_match:
                matched = re_match.group()
                dice_name = f"dice{len(self.dice_list)}"
                self.parsed_expr = self.parsed_expr.replace(matched, dice_name, 1)
                dice_parse = self.parse_dice(matched)
                self.dice_list.append(Dice(dice_parse[0], dice_parse[1], dice_parse[2], dice_parse[3], dice_name, matched))
            else:
                break

    def __str__(self):
        if len(self.dice_list) == 0:
            return str(self.raw_expr)
        elif len(self.dice_list) == 1 and re.fullmatch("([1-9]\d*)?[dD]([1-9]\d*)+((([bB]([1-9]\d*)?))|(([pP]([1-9]\d*)?)))?", self.raw_expr):
            return self.dice_list[0].get_roll_detail()
        else:
            eval_expr = self.parsed_expr

            for d in self.dice_list:
                eval_expr = eval_expr.replace(d.name, f"[{d.get_value()}]")

            string = f"{eval_expr} = {self.get_value()}".replace("  ", " ")

            return string

    def parse_dice(self, dice_expr: str):

        # parsing dice count
        match_count = re.search("([1-9]\d*)?[dD]", dice_expr)
        if match_count and (len(match_count.group()) > 1):
            count = int(match_count.group()[:-1])
        else:
            count = 1

        # parsing dice faces
        match_face = re.search("[dD]([1-9]\d*)+", dice_expr)
        if match_face and (len(match_face.group()) > 1):
            face = int(match_face.group()[1:])
        else:
            face = 100

        # parsing bonus dice
        match_bonus = re.search("[bB][1-9]\d*", dice_expr)
        if match_bonus:
            if len(match_bonus.group()) == 1:
                bonus = 1
            else:
                bonus = int(match_bonus.group()[1:])
        else:
            bonus = 0

        # parsing penalty dice
        match_penalty = re.search("[pP][1-9]\d*", dice_expr)
        if match_penalty:
            if len(match_penalty.group()) == 1:
                penalty = 1
            else:
                penalty = int(match_penalty.group()[1:])
        else:
            penalty = 0

        return [count, face, bonus, penalty]

    def get_value(self):
        eval_expr = self.parsed_expr
        for d in self.dice_list:
            eval_expr = eval_expr.replace(d.name, str(d.get_value()))

        try:
            result = restricted_eval(eval_expr)
            return result
        except Exception as e:
            raise ValueError(f"Unable to parse the dice expr: {self.raw_expr}")

    def get_max_value(self):
        eval_expr = self.parsed_expr
        for d in self.dice_list:
            eval_expr = eval_expr.replace(d.name, str(d.get_max_value()))

        try:
            result = restricted_eval(eval_expr, )
            return result
        except Exception as e:
            raise ValueError(f"Unable to parse the dice expr: {self.raw_expr}")

    def get_min_value(self):
        eval_expr = self.parsed_expr
        for d in self.dice_list:
            eval_expr = eval_expr.replace(d.name, str(d.get_min_value()))

        try:
            result = restricted_eval(eval_expr, )
            return result
        except Exception as e:
            raise ValueError(f"Unable to parse the dice expr: {self.raw_expr}")