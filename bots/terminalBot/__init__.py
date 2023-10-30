import json
import logging
import asyncio

from libs.message import *
from libs.bot import *

from commands.command import command_manager


class TerminalBot(Bot, ABC):
    def run(self):
        super().run()
        logging.info("Terminal Ready")

        while (True):
            msg = input()
            self.receive_message(msg)

    def receive_message(self, msg: str):
        rcvd_msg = self.parse_message(msg)

        logging.received_message(f"[Terminal] {msg}")

        command_manager.run_command(self, rcvd_msg)

    def parse_message(self, msg: str) -> Message:
        ctx = Context()
        ctx.Direction = Context.Direction.INCOMING
        ctx.sender_id = 0
        ctx.sender_name = "[TERMINAL]"

        rcvd_msg = Message(context = ctx)

        rcvd_msg.add_component(Text(msg))

        return rcvd_msg

    async def send_message(self, msg: Message, use_quote: bool = True) -> None:
        msg.context.recipient_id = 0
        msg.context.recipient_name = "[TERMINAL]"


        logging.send_message(f"[Terminal] {msg}")

    async def reply_message(self, msg: Message, content: MessageComponent | list[MessageComponent] | str, use_quote: bool = True) -> None:
        msg_out = Message(context = msg.context.duplicate(), components = content)

        await self.send_message(msg_out, use_quote)

    def shutdown(self):
        pass
        super().shutdown()

TermBot = TerminalBot()