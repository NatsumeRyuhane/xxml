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


@Command(command_name = "switch", aliases = ["sw"], command_group = "coc")
async def switch(bot: Bot, msg: Message):

    async def switch_successful():
        if isinstance(bot, MiraiBot):
            await bot.reply_message(msg, f"{msg.context.sender_name}切换角色「{cm.get_player_current_character(msg.context.sender_id).name}」成功")
        elif isinstance(bot, KOOKBot):
            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(
                            f"{msg.author.nickname}切换角色「{cm.get_player_current_character(msg.author_id).name}」成功"),
                        theme = khl.card.Types.Theme.SUCCESS
                    )
                )
            )

    async def not_your_character_card_warning():
        if isinstance(bot, MiraiBot):
            await bot.reply_message(msg, f"但...这不是属于你的角色卡")
        elif isinstance(bot, KOOKBot):
            await msg.reply(
                khl.card.CardMessage(
                    khl.card.Card(
                        khl.card.Module.Header(f"但...这不是属于你的角色卡"),
                        khl.card.Module.Context(f"如果你确定使用这张角色卡，请务必确定角色卡所属玩家知情并同意"),
                        theme = khl.card.Types.Theme.WARNING
                    )
                ),
                use_quote = False
            )

    parser = CommandParser(add_help = False)
    parser.add_argument("target", nargs = "?", default = None)
    target = None

    try:
        args = shlex.split(msg.get_texts())
        args = parser.parse_args(args[1:])
        try:
            char_id = int(args.target)
            cm.switch_character_by_id(msg.context.sender_id, char_id)
            await switch_successful()

            if cm.get_player_current_character(msg.context.sender_id).owner_id != msg.context.sender_id:
                await not_your_character_card_warning()

        except ValueError:
            character_list = cm.get_character_by_name(args.target)
            if character_list is not []:
                if len(character_list) == 1:
                    cm.switch_character_by_id(msg.context.sender_id, character_list[0].id)
                    await switch_successful()

                    if cm.get_player_current_character(msg.context.sender_id).owner_id != msg.context.sender_id:
                        await not_your_character_card_warning()
                else:
                    if isinstance(bot, MiraiBot):
                        await bot.reply_message(msg, "因为存在重名角色卡的关系，通过角色名切换角色失败...\n\n(可以尝试使用.ls获取你的角色卡ID并通过ID切换角色)")
                    elif isinstance(bot, KOOKBot):
                        await msg.reply(
                            khl.card.CardMessage(
                                khl.card.Card(
                                    khl.card.Module.Header(f"因为存在重名角色卡的关系，通过角色名切换角色失败..."),
                                    khl.card.Module.Context(f"可以尝试使用.ls获取你的角色卡ID并通过ID切换角色"),
                                    theme = khl.card.Types.Theme.WARNING
                                )
                            )
                        )

                    return
            else:
                if isinstance(bot, MiraiBot):
                    await bot.reply_message(msg, "切换角色失败...\n请检查你输入的角色名或角色卡ID是否正确")
                elif isinstance(bot, KOOKBot):
                    await msg.reply(
                        khl.card.CardMessage(
                            khl.card.Card(
                                khl.card.Module.Header(f"切换角色失败..."),
                                khl.card.Module.Context(f"请检查你输入的角色名或角色卡ID是否正确"),
                                theme = khl.card.Types.Theme.DANGER
                            )
                        )
                    )
    except Exception as e:
        pass