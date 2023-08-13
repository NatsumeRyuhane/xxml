import re
from enum import Enum

import libs.dice as dice
import commands.coc.character as character

class SuccessLevel(Enum):
    CRIT_FAILURE = 0
    FAILURE = 1
    SUCCESS = 2
    DIFFICULT_SUCCESS = 3
    LIMITAL_SUCCESS = 4
    CRIT_SUCCESS = 5

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other
        else:
            raise NotImplementedError

class Check():
    def __init__(self, char: character.Character = None, property_name: str = "", property_value: int = None,
                 dice_expression: str = "1d100"):

        property_modify_re = "\+((([1-9]\d*)?[dD]([1-9]\d*)+((([bB]([1-9]\d*)?))|(([pP]([1-9]\d*)?)))?)|\d+|)|-(([1-9]\d*)?[dD]([1-9]\d*)+((([bB]([1-9]\d*)?))|(([pP]([1-9]\d*)?)))?|\d+)"
        matched = re.search(property_modify_re, property_name)
        self.property_value_modifier = dice.DiceExpression("0")
        if matched:
            property_name = property_name.replace(matched.group(), "")
            self.property_value_modifier = dice.DiceExpression(matched.group())

        self.property_name = character.Character.match_property_name(property_name)
        self.character = char

        if self.character is not None:
            self.property_value = self.character.get(self.property_name)
        else:
            self.property_value = property_value

        self.dice_expression = dice_expression

        self.outcome = None
        self.outcome_value = None
        self.result_level = None
        self.run_check()

    def run_check(self):
        self.outcome = dice.DiceExpression(self.dice_expression)
        self.outcome_value = self.outcome.get_value()

        success_rate = self.property_value + self.property_value_modifier.get_value()

        if success_rate >= 50:
            critical_success = 5
            critical_failure = 100
        else:
            critical_success = 1
            critical_failure = 95

        if 1 <= self.outcome_value <= critical_success:
            self.result_level = SuccessLevel.CRIT_SUCCESS
        elif critical_success < self.outcome_value <= int(success_rate / 5):
            self.result_level = SuccessLevel.LIMITAL_SUCCESS
        elif int(success_rate / 5) < self.outcome_value <= int(success_rate / 2):
            self.result_level = SuccessLevel.DIFFICULT_SUCCESS
        elif int(success_rate / 2) < self.outcome_value <= success_rate:
            self.result_level = SuccessLevel.SUCCESS
        elif success_rate < self.outcome_value < critical_failure:
            self.result_level = SuccessLevel.FAILURE
        else:
            self.result_level = SuccessLevel.CRIT_FAILURE
