from commands.command import *
from libs.message import *
from libs.bot import Bot


@Command(command_name = "help", help_short = "显示指令列表")
async def help(bot: Bot, msg: Message):
    parser = CommandParser(add_help = False)
    parser.add_argument("targetCommand", nargs = "?", default = "help")

    try:
        args = shlex.split(msg.get_texts())
        args = parser.parse_args(args[1:])
    except SystemExit:
        await bot.reply_message(msg, Text("指定查询的命令名有点问题...可能是你手癌了？还是你有参数没输完整？"))
        return -1

    async def get_help():
        help_string = "可用指令："
        for c in command_manager.command_dict.keys():
            help_string += f"\n\n[ {command_manager.command_prefix}{c} ]"
            command_help_short = command_manager.command_dict[c][1].help
            if command_help_short:
                help_string += f"\n{command_help_short}"

        await bot.reply_message(msg, Text(f"{help_string}"))

    if args.targetCommand:
        if args.targetCommand == "help":
            await get_help()

        elif command_manager.is_registered_command(args.targetCommand):
            help_string = command_manager.get_command_complex(args.targetCommand)[0].__doc__
            command = str(args.targetCommand).replace(command_manager.command_prefix, '')

            if help_string is None:
                await bot.reply_message(msg, Text(
                    f"{command_manager.command_prefix}{command}\n\n 该指令还没有详细文档。因为小毛龙是懒狗。"))
            else:
                await bot.reply_message(msg, Text(f"{command_manager.command_prefix}{command}\n\n {help_string}"))
            return 0
        elif command_manager.is_command_alias(args.targetCommand):
            help_string = command_manager.get_command_complex(args.targetCommand)[0].__doc__
            command = str(args.targetCommand).replace(command_manager.command_prefix, '')

            if help_string is None:
                await bot.reply_message(msg, Text(
                    f"[{command_manager.command_prefix}{command}]是[{command_manager.command_prefix}{command_manager.command_alias_dict[args.targetCommand]}]的别称。\n\n 该指令还没有详细文档。因为小毛龙是懒狗。"))
            else:
                await bot.reply_message(msg, Text(
                    f"[{command_manager.command_prefix}{command}]是[{command_manager.command_prefix}{command_manager.command_alias_dict[args.targetCommand]}]的别称。\n\n {command_manager.get_command_complex(args.targetCommand)[0].__doc__}"))
            return 0
    else:
        await get_help()