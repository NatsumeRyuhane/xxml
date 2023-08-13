import json
import random
import re
import traceback
import asyncio

import discord
from discord.ext import commands

from libs import util
from libs import log as logging

# TODO: This whole character management shit and integrate with other parts of this module
class Character:
    ID = 0

    def __init__(self):
        self.charName = None
        self.player = None
        self.status = None
        self.attributes = None
        self.inventory = None
        self.character['ID'] = 0
        self.character['Name'] = ""
        self.character['Player'] = ""
        self.character['Status'] = {}
        self.character['Attributes'] = {}
        self.character['Inventory'] = {}

    def create_character(self):
        pass

    def load_character(self, character_file, requested_user):
        character_file = open(character_file, 'r', encoding ='utf-8')
        character = json.loads(character_file.read(), encoding ='utf-8')
        if self.character['player'] != requested_user:
            return "干啥呢你！这卡又不是你的，咬死你哦！"
        else:
            self.character = character
            return f"从现在起你就是{self.character['Name']}啦~"

    def save(self):
        self.character = {'ID': self.ID, 'Name': self.charName, 'Player': self.player, 'Status': self.status,
                          'Attributes': self.attributes, 'Inventory': self.inventory}
        character_file = open('%s.character.json' % self.ID, 'w+', encoding = 'utf-8')
        character_file.write(json.dumps(self.character, indent = 4, separators = (',', ':')))
        character_file.close()


class Dice:

    def __init__(self, dice_expression =''):
        self.rollCount = 0
        self.faces = 0
        self.alternationType = None
        self.alternationRollCount = None
        self.result = []
        self.alternationRollResults = []
        self.diceExpr = dice_expression
        if self.diceExpr[0] == 'd': self.diceExpr = '1' + self.diceExpr
        self.parse_dice_expression()
        self.roll()

    def parse_dice_expression(self):
        if re.match('[1-9][0-9]*d[1-9][0-9]*([bp])*[0-9]*', self.diceExpr):
            self.rollCount = int(re.search('[1-9][0-9]*d', self.diceExpr).group()[:-1])
            self.faces = int(re.search('d[1-9][0-9]*', self.diceExpr).group()[1:])

            self.alternationType = re.search('[bp]', self.diceExpr)
            if self.alternationType is not None:
                self.alternationType = str(self.alternationType.group())

                self.alternationRollCount = re.search('([bp])[0-9]*', self.diceExpr)
                if self.alternationRollCount is not None:
                    self.alternationRollCount = int(self.alternationRollCount.group()[1:])

    def roll(self):
        if self.faces <= 0 or self.rollCount <= 0:
            raise ValueError

        for i in range(0, self.rollCount):
            self.result.append(random.randint(1, self.faces))

        if self.alternationType is not None:
            if self.alternationRollCount == 0:
                raise ValueError

            for i in range(0, self.alternationRollCount):
                self.alternationRollResults.append(random.randint(0, int(self.faces / 10)))

    def calculate_sum_of_result(self):
        return sum(self.result)

    def calculate_altered_result(self):
        if len(self.result) != 1:
            raise NotImplementedError

        if self.alternationType is None:
            raise ValueError

        elif self.alternationType == 'b':
            return [min([self.result[0], min(self.alternationRollResults) * 10 + self.result[0] % 10]),
                    min(self.alternationRollResults)]
        elif self.alternationType == 'p':
            return [
                min([max([self.result[0], max(self.alternationRollResults) * 10 + self.result[0] % 10]), self.faces]),
                max(self.alternationRollResults)]
        else:
            raise ValueError

    def generate_final_result(self):
        if self.alternationType is None:
            return self.calculate_sum_of_result()
        else:
            return int(self.calculate_altered_result()[0])

    def generate_response(self):
        response = ''
        response += f"> {self.diceExpr} = "
        if self.rollCount == 1:
            response += f"**{self.result[0]}**\n"
        else:
            response += "["
            for results in self.result:
                response += f" {results},"
            response = response[:-1] + "]\n"
            response += f"> 合计：**{self.calculate_sum_of_result()}**\n"

        if self.alternationType == 'b':
            altered_result = self.calculate_altered_result()
            response += f"> 奖励骰: {self.alternationRollCount}d{int(self.faces / 10)} ="
            if self.alternationRollCount == 1:
                response += f" **{self.alternationRollResults[0]}**\n"
            else:
                response += " ["
                for altResults in self.alternationRollResults:
                    if altResults == altered_result[1]:
                        response += f" **{altResults}**,"
                    else:
                        response += f" {altResults},"
                response = response[:-1] + f"] = **{altered_result[1]}**\n"
            response += f"> 最终结果：**{altered_result[0]}**\n"

        elif self.alternationType == 'p':
            altered_result = self.calculate_altered_result()
            response += f"> 惩罚骰: {self.alternationRollCount}d{int(self.faces / 10)} ="
            if self.alternationRollCount == 1:
                response += f" **{self.alternationRollResults[0]}**\n"
            else:
                response += " ["
                for altResults in self.alternationRollResults:
                    if altResults == altered_result[1]:
                        response += f" **{altResults}**,"
                    else:
                        response += f" {altResults},"
                response = response[:-1] + f"] = **{altered_result[1]}**\n"
            response += f"> 最终结果：**{altered_result[0]}**\n"

        response += "\n"
        return response


class CoC(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Command(aliases = ['r'])
    async def roll(self, context, dice_expression =""):
        response = context.message.author.mention + "的掷骰结果：\n\n"
        try:
            dice_count = 0

            while True:
                current_dice_expression = None
                current_dice_expression = re.search('[0-9]*d[1-9][0-9]*([bp])*[1-9]*[0-9]*', dice_expression)

                if current_dice_expression is not None:
                    dice = Dice(current_dice_expression.group())
                    response += dice.generate_response()
                    dice_expression = dice_expression.replace(current_dice_expression.group(), str(dice.generate_final_result()))
                    dice_count += 1

                else:
                    break

            if dice_count == 0:
                raise ValueError(f"Invalid dice expression {dice_expression}")

            if dice_count == 1:
                if str(dice_expression) == str(eval(dice_expression)):
                    response += f"合计：**{eval(dice_expression)}**"
                else:
                    response += f"合计：{dice_expression} = **{eval(dice_expression)}**"

            else:
                response += f"合计：{dice_expression} = **{eval(dice_expression)}**"

            await context.send(response)
            await logging.info(None, None, 'roll', response, dice_expression, str(context.message.author))
            return eval(dice_expression)

        except ValueError:
            await context.send("这个骰子表达式写的有问题，建议重写")
            await logging.info("Invalid dice expression detected", traceback.format_exc(), 'roll',
                               "这个骰子表达式写的有问题，建议重写", dice_expression, str(context.message.author))

        except SyntaxError:
            await context.send("这个骰子表达式写的有问题，建议重写")
            await logging.info("Invalid dice expression detected", traceback.format_exc(), 'roll',
                               "这个骰子表达式写的有问题，建议重写", dice_expression, str(context.message.author))

        except NotImplementedError:
            await context.send("多个骰子表达式不能上奖惩骰子...因为没定义。如果实在需要的话可以告诉小毛龙让他帮你写一个~")
            await logging.info("Invalid dice expression detected", traceback.format_exc(), 'roll',
                               "多个骰子表达式不能上奖惩骰子...因为没定义。如果实在需要的话可以告诉小毛龙让他帮你写一个~",
                               dice_expression, str(context.message.author))

        except Exception:
            await logging.error("Exception when executing command", traceback.format_exc(), 'roll', response,
                                dice_expression,
                                str(context.message.author))
            await context.send("好像哪里出错了！小毛龙过一会大概会试着修一下！")

    @commands.Command(aliases = ['ra'])
    async def rc(self, context, attribute_name ="[未命名属性]", *, attribute_value = 1, alternation_expression = ""):
        response = f"{context.message.author.mention}的{attribute_name}检定({attribute_value})结果：\n\n"
        if True:
            await context.send("这个还没做好！小毛龙不知道这里怎么写，建议让黑曜来写", file = util.reaction(6))
        if False:
            # TODO:从角色卡读取技能数值
            pass
        else:
            try:
                dice = Dice('1d100' + alternation_expression)
                response += dice.generate_response()

                result = dice.generate_final_result()
                if 0 < result <= 5:
                    pass
                elif 5 < result <= attribute_value / 5:
                    pass
                elif attribute_value / 5 < result <= attribute_value / 2:
                    pass
                elif attribute_value / 2 < result <= attribute_value:
                    pass
                elif attribute_value < result <= 95:
                    pass
                elif 95 < result <= 100:
                    pass
                else:
                    pass

                await context.send(response)
                await logging.info(None, traceback.format_exc(), 'roll', response,
                                   [attribute_name, attribute_value, alternation_expression],
                                   str(context.message.author))
            except Exception:
                await logging.error("Exception when executing command", traceback.format_exc(), 'rc', response,
                                    [attribute_name, attribute_value, alternation_expression],
                                    str(context.message.author))
                await context.send("好像哪里出错了！小毛龙过一会大概会试着修一下！")


def setup(client):
    client.add_cog(CoC(client))