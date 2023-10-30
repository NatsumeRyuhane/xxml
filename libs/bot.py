import asyncio


from abc import ABC, abstractmethod

from libs.message import Message, MessageComponent
from libs.event import Event


class Bot(ABC):
    """
    abc for all bot instances
    this class specifies all interfaces that the bot should implement
    """

    def __init__(self):
        self.instance = None
        self.event_loop = None

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        return self.event_loop

    def run(self):
        """
        starts the bot
        """
        try:
            self.event_loop = asyncio.get_event_loop()
        except RuntimeError:
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)

    def shutdown(self):
        raise Exception

    @abstractmethod
    def receive_message(self, msg):
        """
        message receiver
        """
        pass

    @abstractmethod
    def parse_message(self, msg) -> Message:
        """
        parse the message received to a Message object
        """
        pass

    @abstractmethod
    async def send_message(self, msg: Message, use_quote: bool = False) -> None:
        """
        send the message as the details specified in the Message object
        """
        pass

    @abstractmethod
    async def reply_message(self, msg: Message, content: MessageComponent | list[MessageComponent] | str, use_qoute: bool = True) -> None:
        """
        """

    # TODO
    # @abstractmethod
    def receive_event(self, event):
        pass

    # @abstractmethod
    def parse_event(self, event) -> Event:
        pass

    # @abstractmethod
    def transcribe_message(self, msg: Message):
        """
        save message to a database
        """
        pass