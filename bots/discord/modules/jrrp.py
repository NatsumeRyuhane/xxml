import traceback
import json
import random
import asyncio

from discord.ext import commands

from libs import util
from libs import log as logging


class BasicCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Command()
    async def jrrp(self, context):
        try:
            record_dict = {}
            reaction = None

            record_file = open("./data/coc/jrrp/jrrp.record", 'a+', encoding='utf-8')
            record_file.seek(0, 0)

            if record_file.read() == '':
                record_dict['Date'] = util.get_current_time()[:10]
            else:
                record_file.seek(0, 0)
                record_dict = json.loads(record_file.read())

                # Check if the record file is outdated
                if record_dict['Date'] != util.get_current_time()[:10]:
                    record_dict.clear()
                    record_dict['Date'] = util.get_current_time()[:10]
                    record_file.seek(0, 0)
                    record_file.truncate()

            try:
                record_res = record_dict[str(context.message.author)]
                response = "你今天明明就检定过了 莫不是想要逆天改命...反正我是不会给你改的\n"
                response += record_res

            except KeyError:
                easter_egg_ref_val = random.randint(3, 98)
                jrrp = random.randint(25, 75)
                check_value = random.randint(1, 100)

                if check_value - 2 <= easter_egg_ref_val <= check_value + 2:
                    with open("./data/coc/jrrp/items.json", 'r', encoding='utf-8') as itemFile:
                        itemFile.seek(0, 0)
                        item_dict = json.loads(itemFile.read())
                        item_index = random.randint(0, len(item_dict["items"]) - 1)
                        item = item_dict["items"][item_index]
                        response = f"{context.message.author.mention}今天的rp检定结果是：{item['title']}\n"
                        response += f"{item['description']}"

                        try:
                            image_file = util.generate_discord_py_file_object(f"./data/jrrp/jrrp_item_images/{item['image_name']}")
                        except KeyError:
                            image_file = None
                        if image_file is None:
                            msg = await context.send(response)
                        else:
                            msg = await context.send(response, file=image_file)

                        await asyncio.sleep(5)
                        await msg.edit(content=f"~~{response}~~")
                        await logging.error("Easter egg triggered in command jrrp", None, 'jrrp',
                                            response, None, str(context.message.author))

                response = f"{context.message.author.mention}今天的rp检定结果是：**{str(check_value)}** "
                response_list = []
                if 0 < check_value <= 5:
                    response += "[**大成功**]\n"
                    response_list = ["哇，哇哦...", "草 这不科学 让我重新来一次", "？"]
                    reaction = util.reaction(0)
                elif 5 < check_value <= jrrp / 5:
                    response += "[**极难成功**]\n"
                    response_list = ["tql wsl", "运气这么好不去跑个团？"]
                    reaction = util.reaction(5)
                elif jrrp / 5 < check_value <= jrrp / 2:
                    response += "[**困难成功**]\n*"
                    response_list = ["不错不错 牛逼牛逼", "公招出五星程度的运气", "今天适合在群里整活而不至于被打死噢"]
                    reaction = util.reaction(8)
                elif jrrp / 2 < check_value <= jrrp:
                    response += "[**成功**]\n"
                    response_list = ["我觉得海星", "一般般啦——", "*毛龙打了个滚。*"]
                elif jrrp < check_value <= 95:
                    response += "[**失败**]\n"
                    response_list = ["噗嗤", "不愧是你", "就这？"]
                    reaction = util.reaction(3)
                elif 95 < check_value <= 100:
                    response += "[**大失败**]\n"
                    response_list = ["建议去当KP", "就是宁一脚把线索踩烂了？建议击毙@平安CoC", "这人抽卡必歪五个六星"]
                    reaction = util.reaction(4)

                response = util.append_random_string(response_list, response)

                record_dict[str(context.message.author)] = response
                record_file.seek(0, 0)
                record_file.truncate()
                record_file.write(json.dumps(record_dict, indent=4, separators=(',', ':')))

            record_file.close()
            if reaction is not None:
                await context.send(response, file=reaction)
            else:
                await context.send(response)
            await logging.info(None, None, 'jrrp', response, str(context.message.author))

        except Exception:
            await logging.error("Exception occurred while executing command jrrp", traceback.format_exc(), 'jrrp', None,
                                str(context.message), str(context.message.author))
            await context.send("好像哪里出错了！小毛龙过一会大概会试着修一下！", file=util.reaction(6))

    @commands.Command()
    async def jjrp(self, context):
        response = ""
        response_list = \
            [
                f"妈妈 有鸡{context.message.author.mention}",
                f"jjrp!",
                f"？",
                f"你有问题...",
                f"jrrp!"
            ]
        await context.send(util.append_random_string(response_list, response), file=util.reaction(3))


def setup(client):
    client.add_cog(BasicCommands(client))
