from commands.command import *
from libs.message import *
from libs.bot import Bot


@Command(command_name = "imgecho")
async def ping(bot: Bot, msg: Message):
    await bot.reply_message(msg, [
        Quote(msg.context.msg_id),
        "已设置CA。我会复读你的下一条消息里的图片...如果有的话。"
    ])

    ca = command_manager.set_context_actions(msg, ContextActions.ContextActionType.ON_NEXT_MESSAGE)

    @ca.add_action()
    async def repeat(bot: Bot, msg: Message):
        image_components = []

        for mc in msg.components:
            if isinstance(mc, Image):
                image_components.append(mc)

        if image_components:
            await bot.reply_message(msg, image_components)

        command_manager.clear_context_action(msg)
