import json
import logging

from libs.message import *
from libs.bot import *

import bots.mirai.miraicle as miraicle
from commands.command import command_manager


class MiraiBot(Bot, ABC):
    def run(self):
        super().run()
        self.instance.run()

    def receive_message(self, msg: miraicle.Message):
        rcvd_msg = self.parse_message(msg)

        if rcvd_msg.context.context_type == Context.MessageContextType.GROUP:
            logging.received_message(f"[Mirai] [Group  ] \"{rcvd_msg.context.guild_name}\"({rcvd_msg.context.guild_id}) - \"{rcvd_msg.context.sender_name}\"({rcvd_msg.context.sender_id}): {rcvd_msg}")
        if rcvd_msg.context.context_type == Context.MessageContextType.QQ_TEMP:
            logging.received_message(f"[Mirai] [Temp   ] \"{rcvd_msg.context.guild_name}\"({rcvd_msg.context.guild_id}) - \"{rcvd_msg.context.sender_name}\"({rcvd_msg.context.sender_id}): {rcvd_msg}")
        if rcvd_msg.context.context_type == Context.MessageContextType.PRIVATE:
            logging.received_message(f"[Mirai] [PRIVATE] \"{rcvd_msg.context.sender_name}\"({rcvd_msg.context.sender_id}): {rcvd_msg}")

        command_manager.run_command(self, rcvd_msg)

    def parse_message(self, msg: miraicle.Message) -> Message:
        ctx = Context()
        ctx.Direction = Context.Direction.INCOMING

        # parse message context
        if isinstance(msg, miraicle.GroupMessage):
            ctx.MessageContextType = Context.MessageContextType.GROUP
            ctx.msg_id = msg.id
            ctx.guild_id = msg.group
            ctx.guild_name = msg.group_name
            ctx.sender_id = msg.sender
            ctx.sender_name = msg.sender_name
        elif isinstance(msg, miraicle.FriendMessage):
            ctx.MessageContextType = Context.MessageContextType.PRIVATE
            ctx.msg_id = msg.id
            ctx.sender_id = msg.sender
            ctx.sender_name = msg.sender_name
        elif isinstance(msg, miraicle.TempMessage):
            ctx.MessageContextType = Context.MessageContextType.QQ_TEMP
            ctx.msg_id = msg.id
            ctx.guild_id = msg.group
            ctx.guild_name = msg.group_name
            ctx.sender_id = msg.sender
            ctx.sender_name = msg.sender_name

        rcvd_msg = Message(context = ctx)

        try:
            if msg.json["messageChain"][1]['type'] == "Quote":
                rcvd_msg.add_component(Quote(target_message_id = msg.json["messageChain"][1]['id']))
        except Exception:
            pass

        for m in msg.chain:
            if isinstance(m, miraicle.Plain):
                rcvd_msg.add_component(Text(m.text))
            elif isinstance(m, miraicle.At):
                rcvd_msg.add_component(At(target = m.qq, target_name = m.display))
            elif isinstance(m, miraicle.AtAll):
                rcvd_msg.add_component(AtAll())
            elif isinstance(m, miraicle.Face):
                pass
            elif isinstance(m, miraicle.Image):
                rcvd_msg.add_component(Image(base64 = m.base64, url = m.url))
            elif isinstance(m, miraicle.FlashImage):
                rcvd_msg.add_component(Image(base64 = m.base64, url = m.url))
            elif isinstance(m, miraicle.Voice):
                rcvd_msg.add_component(Audio(base64 = m.base64, url = m.url))
            elif isinstance(m, miraicle.Xml):
                pass
            elif isinstance(m, miraicle.Json):
                pass
            elif isinstance(m, miraicle.App):
                pass
            elif isinstance(m, miraicle.Poke):
                pass
            elif isinstance(m, miraicle.Dice):
                pass
            elif isinstance(m, miraicle.File):
                pass
            else:
                pass

        return rcvd_msg

    async def send_message(self, msg: Message, use_quote: bool = True) -> None:
        msg_out = []
        quote_msg_id = None

        for mmc in msg.meta:
            if isinstance(mmc, Quote):
                quote_msg_id = mmc.target_message_id
            else:
                pass

        for mc in msg.components:
            if isinstance(mc, Text):
                msg_out.append(miraicle.Plain(mc.content))
            elif isinstance(mc, Image):
                msg_out.append(miraicle.Image(base64 = mc.base64))
            elif isinstance(mc, At):
                msg_out.append(miraicle.At(qq = mc.target))
            elif isinstance(mc, AtAll):
                msg_out.append(miraicle.AtAll())
            else:
                pass

        if isinstance(self, SyncMiraiBot):
            if msg.context.context_type == Context.MessageContextType.GROUP:
                self.instance.send_group_msg(
                    group = msg.context.guild_id,
                    msg = msg_out,
                    quote = quote_msg_id
                )
            elif msg.context.context_type == Context.MessageContextType.PRIVATE:
                self.instance.send_friend_msg(
                    qq = msg.context.recipient_id,
                    msg = msg_out
                )
            elif msg.context.context_type == Context.MessageContextType.QQ_TEMP:
                self.instance.send_temp_msg(
                    group = msg.context.guild_id,
                    qq = msg.context.recipient_id,
                    msg = msg_out
                )
            else:
                raise NotImplementedError()
        elif isinstance(self, AsyncMiraiBot):
            if msg.context.context_type == Context.MessageContextType.GROUP:
                await self.instance.send_group_msg(
                        group = msg.context.guild_id,
                        msg = msg_out,
                        quote = quote_msg_id
                    )
            elif msg.context.context_type == Context.MessageContextType.PRIVATE:
                await self.instance.send_friend_msg(
                        qq = msg.context.recipient_id,
                        msg = msg_out
                    )
            elif msg.context.context_type == Context.MessageContextType.QQ_TEMP:
                await self.instance.send_temp_msg(
                        group = msg.context.guild_id,
                        qq = msg.context.recipient_id,
                        msg = msg_out
                    )
            else:
                raise NotImplementedError()
        else:
            pass

        if msg.context.context_type == Context.MessageContextType.GROUP:
            logging.send_message(f"[Mirai] [Group  ] \"{msg.context.guild_name}\"({msg.context.guild_id}): {msg}")
        if msg.context.context_type == Context.MessageContextType.QQ_TEMP:
            logging.send_message(f"[Mirai] [Temp   ] \"{msg.context.guild_name}\"({msg.context.guild_id}): {msg}")
        if msg.context.context_type == Context.MessageContextType.PRIVATE:
            logging.send_message(f"[Mirai] [PRIVATE] \"{msg.context.recipient_id}\"({msg.context.recipient_name}): {msg}")

    async def reply_message(self, msg: Message, content: MessageComponent | list[MessageComponent] | str, use_quote: bool = True) -> None:
        if isinstance(content, MessageComponent):
            content = [content]
        if isinstance(content, str):
            content = [Text(content)]

        msg_out = Message(context = msg.context.duplicate(), components = content)

        msg_out.context.recipient_id = msg.context.sender_id
        msg_out.context.sender_id = self.instance.qq
        msg_out.context.direction = Context.Direction.OUTGOING

        if use_quote:
            msg_out.add_component(Quote(target_message_id = msg.context.msg_id))
            msg_out.add_component(Text(" "))

        await self.send_message(msg_out, use_quote)

    def shutdown(self):
        pass
        super().shutdown()

class SyncMiraiBot(MiraiBot):

    def __init__(self, instance: miraicle.Mirai) -> None:
        super().__init__()
        logging.info("Initializing Mirai Bot...")
        self.instance = instance
        self.start_func = instance.run

        if not isinstance(self.instance, miraicle.Mirai):
            raise ValueError("Wrong bot type!")

        @miraicle.Mirai.receiver('GroupMessage')
        def gm(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
            self.receive_message(msg)

        @miraicle.Mirai.receiver('FriendMessage')
        def fm(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
            self.receive_message(msg)

        @miraicle.Mirai.receiver('TempMessage')
        def tm(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
            self.receive_message(msg)

    def run(self):
        super().run()
        logging.info("Starting Mirai bot")

class AsyncMiraiBot(MiraiBot):

    def __init__(self, instance: miraicle.AsyncMirai) -> None:
        super().__init__()
        logging.info("Initializing AsyncMirai Bot...")
        self.instance = instance
        self.start_func = instance.run

        if not isinstance(self.instance, miraicle.AsyncMirai):
            raise ValueError("Wrong bot type!")

        @miraicle.AsyncMirai.receiver('GroupMessage')
        def gm(bot: miraicle.AsyncMirai, msg: miraicle.GroupMessage):
            self.receive_message(msg)

        @miraicle.AsyncMirai.receiver('FriendMessage')
        def fm(bot: miraicle.AsyncMirai, msg: miraicle.GroupMessage):
            self.receive_message(msg)

        @miraicle.AsyncMirai.receiver('TempMessage')
        def tm(bot: miraicle.AsyncMirai, msg: miraicle.GroupMessage):
            self.receive_message(msg)

    def run(self):
        logging.info("Starting AsyncMirai bot")
        super().run()


try:
    with open("./bots/mirai/config.json") as f:
        configs = json.load(f)

        AsyncMirai = AsyncMiraiBot(instance = miraicle.AsyncMirai(qq = configs["qq"], verify_key = configs["mirai_verify_key"], host = configs["mirai_host"], port = configs["mirai_port"]))
        Mirai = SyncMiraiBot(instance = miraicle.Mirai(qq = configs["qq"], verify_key = configs["mirai_verify_key"], host = configs["mirai_host"], port = configs["mirai_port"]))
except FileNotFoundError:
    logging.error("no config file found")
