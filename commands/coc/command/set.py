from commands.command import Command, CommandParser

from libs.bot import Bot
from libs.message import *
import libs.dice as dice

from bots.mirai import MiraiBot
from bots.kook import KOOKBot
import bots.kook.khl as khl

import shlex

import commands.coc.character as character
from commands.coc.character import character_manager as cm


@Command(command_name = "set", aliases = ["st"], command_group = "coc", help_short = "设置角色卡属性")
async def st(bot: Bot, msg: Message):
    try:
        args = shlex.split(msg.get_texts())

        char = cm.get_player_current_character(msg.context.sender_id)
        if char is None:
            cm.add_character(msg.context.sender_name, msg.context.sender_id)
            char = cm.get_player_current_character(msg.context.sender_id)

            if isinstance(bot, MiraiBot):
                await bot.reply_message(msg, content = [
                    Text(f"你好，{msg.context.sender_name}!\n\n已自动创建并使用新的角色卡。后续请使用 .nn 为角色卡命名。\n\n这张角色卡的ID为{cm.get_player_current_character(msg.context.sender_id).id}")
                ])
            else:
                await msg.reply(
                    khl.card.CardMessage(
                        khl.card.Card(
                            khl.card.Module.Header(f"你好，{msg.author.nickname}"),
                            khl.card.Module.Context(
                                f"已自动创建并使用新的角色卡。后续请使用 .nn 为角色卡命名。\n\n这张角色卡的ID为{cm.get_player_current_character(msg.author_id).id}"),
                            theme = khl.card.Types.Theme.SUCCESS
                        )
                    ),
                    use_quote = False
                )

        properties_list = args[1:]
        properties = ""
        for p in properties_list:
            properties += p

        result = char.set_from_string(properties)

        if isinstance(bot, MiraiBot):
            response = f"更新了「{char.name}」的角色参数"

            if result["created"]:
                count = 1
                response += "\n\n导入了以下属性：\n"
                for c in result["created"]:
                    response += f"{c}  {result['created'][c]}    "
                    count += 1
                    if count % 3 == 0:
                        count = 1
                        response = response[:-4]
                        response += "\n"

            if result["updated"]:
                response += "\n\n更新了以下属性："
                for f in result["updated"]:
                    response += f"\n  {f}  {result['updated'][f][0]} ➔ {result['updated'][f][1]}"

            if result["failed"]:
                response += "\n\n...但是一部分属性的导入失败了："
                for f in result["failed"]:
                    response += f"\n  {f}"

            if result["warnings"]:
                response += "\n\n根据导入的属性，这张角色卡的以下方面可能需要注意："
                for f in result["warnings"]:
                    response += f"\n  「{f}」: {result['warnings'][f]}"

            await bot.reply_message(msg, response)
        elif isinstance(bot, KOOKBot):
            response = khl.card.Card(
                khl.card.Module.Header(f"更新了「{char.name}」的角色参数"),
                theme = khl.card.Types.Theme.SUCCESS
            )

            if result["updated"]:
                updated_prompt = "更新了以下属性：\n"
                for f in result["updated"]:
                    updated_prompt += f"  {f}  {result['updated'][f][0]} ➔ {result['updated'][f][1]}\n"

                response.append(khl.card.Module.Divider())
                response.append(khl.card.Module.Context(updated_prompt))

            if result["failed"]:
                fail_prompt = "...但是一部分属性的导入失败了：\n"
                for f in result["failed"]:
                    fail_prompt += f"  {f}\n"
                response.append(khl.card.Module.Divider())
                response.append(khl.card.Module.Context(fail_prompt))
                response.theme = khl.card.Types.Theme.WARNING
            else:
                response.append(khl.card.Module.Context("\n成功导入/更新了所有输入的属性"))

            if result["warnings"]:
                warn_prompt = "根据导入的属性，这张角色卡的以下方面可能需要注意：\n"
                for f in result["warnings"]:
                    warn_prompt += f"  {f}\n"
                response.append(khl.card.Module.Divider())
                response.append(khl.card.Module.Context(warn_prompt))

            await msg.reply(khl.card.CardMessage(response), use_quote = False)
        else:
            pass
    except (SystemExit, Exception) as e:
        pass
