import json
import logging

from libs.message import *
from libs.bot import *

import khl
from commands.command import command_manager


class KOOKBot(Bot):

    def __init__(self, instance: khl.Bot) -> None:
        super().__init__()

        logging.info("Initializing KOOK Bot...")
        self.instance = instance

        if not isinstance(self.instance, khl.Bot):
            raise ValueError("Wrong bot type!")

        @self.instance.on_message(khl.MessageTypes.SYS)
        async def mr(msg: khl.Message):
            self.receive_message(msg)

    def run(self):
        super().run()
        logging.info("Starting KOOK bot")
        self.instance.run()

    def receive_message(self, msg: khl.Message):
        rcvd_msg = self.parse_message(msg)

        if rcvd_msg.context.context_type == Context.MessageContextType.GROUP:
            logging.received_message(f"[KOOK] [Group  ] \"{rcvd_msg.context.guild_name}\"({rcvd_msg.context.guild_id}) - \"{rcvd_msg.context.channel_name}\"({rcvd_msg.context.channel_id}) - \"{rcvd_msg.context.sender_name}\"({rcvd_msg.context.sender_id}): {rcvd_msg}")
        elif rcvd_msg.context.context_type == Context.MessageContextType.PRIVATE:
            logging.received_message(f"[KOOK] [PRIVATE] \"{rcvd_msg.context.sender_name}\"({rcvd_msg.context.sender_id}): {rcvd_msg}")

        command_manager.run_context_action(self, rcvd_msg)
        command_manager.run_command(self, rcvd_msg)

    def parse_message(self, msg: khl.Message) -> Message: 
        ctx = Context()
        ctx.direction = Context.Direction.INCOMING

        # parse message context
        if isinstance(msg, khl.PublicMessage):
            ctx.MessageContextType = Context.MessageContextType.GROUP
            ctx.msg_id = msg.id
            ctx.guild_id = msg.guild.id
            ctx.guild_name = msg.guild.name
            ctx.channel_id = msg.channel.id
            ctx.channel_name = msg.channel.name
            ctx.sender_id = msg.author.id
            ctx.sender_name = msg.author.nickname
        elif isinstance(msg, khl.PrivateMessage):
            ctx.MessageContextType = Context.MessageContextType.PRIVATE
            ctx.msg_id = msg.id
            ctx.channel_id = msg.channel.id
            ctx.channel_name = None
            ctx.sender_id = msg.author.id
            ctx.sender_name = msg.author.nickname
        else:
            pass

        rcvd_msg = Message(context = ctx)

        if "qoute" in msg.extra.keys():
            rcvd_msg.add_component(Quote(target_message_id = msg.extra["qoute"]["rong_id"]))

        if msg.type == khl.MessageTypes.TEXT:
            rcvd_msg.add_component(Text(msg.content))
        elif msg.type == khl.MessageTypes.IMG:
            rcvd_msg.add_component(Image(url = msg.extra["attachments"]["url"]))
        elif msg.type == khl.MessageTypes.VIDEO:
            rcvd_msg.add_component(Video(url = msg.extra["attachments"]["url"]))
        elif msg.type == khl.MessageTypes.FILE:
            rcvd_msg.add_component(Video(url = msg.extra["attachments"]["url"]))
        elif msg.type == khl.MessageTypes.AUDIO:
            pass
        elif msg.type == khl.MessageTypes.KMD:
            rcvd_msg.add_component(Text(msg.content))
        elif msg.type == khl.MessageTypes.CARD:
            pass
        else:
            pass

        return rcvd_msg

    async def send_message(self, msg: Message, use_quote: bool = True) -> None:
        quote_msg_id = None
        content = None
        content_type = khl.MessageTypes.TEXT

        for mmc in msg.meta:
            if isinstance(mmc, Quote):
                quote_msg_id = mmc.target_message_id
            else:
                pass

        for mc in msg.components:
            if isinstance(mc, Text):
                content = str(mc)
                content_type = khl.MessageTypes.TEXT
            elif isinstance(mc, Image):
                content = None
                content_type = khl.MessageTypes.IMG
            elif isinstance(mc, At):
                pass
            elif isinstance(mc, AtAll):
                pass
            elif isinstance(mc, KOOKCardMessage):
                content = mc.content
                content_type = khl.MessageTypes.CARD
            else:
                pass

        if msg.context.context_type == Context.MessageContextType.GROUP:
            channel = await self.instance.client.fetch_public_channel(msg.context.channel_id)

            if msg.context.visibility == Context.Visibility.PUBLIC:
                await self.instance.client.send(
                    target = channel,
                    content = content,
                    type = content_type
                )
            elif msg.context.visibility == Context.Visibility.PRIVATE:
                await self.instance.client.send(
                    target = channel,
                    content = content,
                    type = content_type,
                    temp_target_id = msg.context.recipient_id
                )

        elif msg.context.context_type == Context.MessageContextType.PRIVATE:
            await self.instance.client.send(
                target = msg.context.recipient_id,
                content = content,
                type = content_type
            )
        else:
            raise NotImplementedError()

    async def reply_message(self, msg: Message, content: MessageComponent | list[MessageComponent] | str, use_quote: bool = True) -> None:
        if isinstance(content, MessageComponent):
            content = [content]

        if isinstance(content, str):
            content = [Text(content)]

        msg_out = Message(context = msg.context.duplicate(), components = content)

        msg_out.context.recipient_id = msg.context.sender_id
        msg_out.context.sender_id = None

        if use_quote:
            msg_out.add_component(Quote(target_message_id = msg.context.msg_id))

        await self.send_message(msg_out, use_quote)

    def shutdown(self):
        super().shutdown()

try:
    with open("./bots/kook/config.json") as f:
        configs = json.load(f)
        KOOK = KOOKBot(instance = khl.Bot(token = configs["token"]))
except FileNotFoundError:
    logging.error("no config file found")
