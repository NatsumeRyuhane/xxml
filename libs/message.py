import copy
from enum import Enum
from abc import abstractmethod, ABC
import base64 as b64

from khl.card.card_message import CardMessage as KOOKCardMsg


class Context:
    class MessageContextType(Enum):
        PRIVATE = 1
        GROUP = 2
        QQ_TEMP = 4

    class Visibility(Enum):
        PUBLIC = 1
        RESTRICTED = 2
        PRIVATE = 4

    class Direction(Enum):
        INCOMING = 1
        OUTGOING = 2

    def __init__(self, msg_id: str = None, context_type: MessageContextType = MessageContextType.GROUP, visibility = Visibility.PUBLIC,
                 direction = Direction.INCOMING,
                 guild_id: str = None, guild_name: str = None,
                 channel_id: str = None, channel_name: str = None,
                 sender_id: str = None, sender_name: str = None,
                 recipient_id:str = None, recipient_name: str = None):
        self.msg_id = msg_id
        self.context_type = context_type
        self.visibility = visibility
        self.direction = direction
        self.guild_id = str(guild_id)
        self.guild_name = str(guild_name)
        self.channel_id = str(channel_id)
        self.channel_name = str(channel_name)
        self.sender_id = str(sender_id)
        self.sender_name = str(sender_name)
        self.recipient_id = str(recipient_id)
        self.recipient_name = str(recipient_name)

    def duplicate(self):
        return copy.deepcopy(self)


class MessageComponent(ABC):

    def __init__(self):
        pass

    @classmethod
    def list_message_components(cls) -> list[str]:

        def get_subclasses(obj, subclasses_list: list) -> bool:
            subclasses = obj.__subclasses__()

            if subclasses:
                for c in subclasses:
                    subclasses_list.append(c.__name__)
                    subclasses_list.append([])
                    if get_subclasses(c, subclasses_list[-1]):
                        pass
                    else:
                        subclasses_list.pop()

                return True
            else:
                return False

        components = []
        get_subclasses(cls, components)
        return components

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class MetaComponent(MessageComponent, ABC):
    """
    meta component does not deliver content, but alters the behavior of a message
    """


class Message:

    def __init__(self, context: Context, components = None) -> None:
        self.context = context
        self.components = []
        self.meta = []

        if components:
            self.add_component(components)

    def __str__(self):
        text = ""
        for c in self.components:
            text += str(c)

        if self.meta:
            return f"{{{self.meta}}} {text}"
        else:
            return f"{text}"

    def add_component(self, component: MessageComponent | str | list[MessageComponent, str]):
        if not isinstance(component, list):
            component = [component]

        for c in component:
            if isinstance(c, MetaComponent):
                self.meta.append(c)
            elif isinstance(c, str):
                self.components.append(Text(c))
            elif isinstance(c, KOOKCardMsg):
                self.components.append(KOOKCardMessage(c))
            else:
                self.components.append(c)

    def get_texts(self) -> str:
        """
        get all texts from the message
        excludes non-Text components
        """
        text = ""
        for c in self.components:
            if isinstance(c, Text):
                text += str(c)
            else:
                pass

        return text


class Quote(MetaComponent):
    """
    a quote meta component indicates this message quotes another message
    """

    def __init__(self, target_message_id: str = None):
        super().__init__()
        self.target_message_id = target_message_id

    def __str__(self):
        return f"[Quote:{self.target_message_id}]"

    def __repr__(self):
        return f"[Quote:{self.target_message_id}]"


class Ethereal(MetaComponent):
    """
    a quote meta component indicates this message should be temporary
    on client that does not support this feature, this meta component has no effect
    """

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"[Ethereal]"

    def __repr__(self):
        return f"[Ethereal]"


class At(MessageComponent):
    def __init__(self, target: str, target_name: str = None):
        super().__init__()
        self.target = target
        self.target_name = target_name

    def __str__(self):
        if self.target_name:
            return f"@{self.target_name}"
        else:
            return f"@{self.target}"

    def __repr__(self):
        return f"[At:{self.target}]"


class AtAll(MessageComponent):
    def __str__(self):
        return f"@ALL"

    def __repr__(self):
        return f"[AtAll]"


class Text(MessageComponent):
    class TextFormatter(ABC):
        pass

    class Bold(TextFormatter):
        pass

    class Italic(TextFormatter):
        pass

    class Underline(TextFormatter):
        pass

    class Code(TextFormatter):
        pass

    class CodeBlock(TextFormatter):
        def __init__(self, language: str = None):
            self.language = language

    class Color(TextFormatter):
        def __init__(self, color_name: str = None, color_hex: str = None):
            self.color_name = color_name
            self.color_hex = color_hex

    def __init__(self, content: str, format: set[TextFormatter] = None):
        super().__init__()
        self.content = content
        self.format = format

    def __str__(self):
        return f"{self.content}"

    def __repr__(self):
        return f"[Text]"

    def to_markdown(self) -> str:
        markdown_str = self.content

        for tf in self.format:
            if isinstance(tf, Text.Bold):
                markdown_str = f"**{markdown_str}**"
            elif isinstance(tf, Text.Italic):
                markdown_str = f"*{markdown_str}*"
            elif isinstance(tf, Text.Underline):
                # TODO
                pass
            elif isinstance(tf, Text):
                markdown_str = f"`{markdown_str}`"
            elif isinstance(tf, Text.CodeBlock):
                markdown_str = f"```{tf.language}\n{markdown_str}\n```"
            elif isinstance(tf, Text.Color):
                # TODO
                pass
            else:
                raise ValueError

        return markdown_str


class MediaComponent(MessageComponent, ABC):
    """
    this type of component contains media files to send, but not in file upload form
    """

    def __init__(self, base64: bytes = None, filepath: str = None, url: str = None):
        super().__init__()
        self.filepath = filepath
        self.base64 = base64
        self.url = url
        self.load()

    def load(self):
        """
        load the message content into base64
        and assign to self.base64
        """
        if self.base64:
            pass
        elif self.filepath:
            self.base64 = b64.b64encode(open(self.filepath, 'rb').read())
        elif self.url:
            pass
        else:
            raise ValueError("No file provided")

    def save(self, filename: str = None, dest: str = None):
        if self.base64:
            raise NotImplementedError()
        elif self.filepath:
            raise NotImplementedError("Jesus WTF?")
        elif self.url:
            raise NotImplementedError()
        else:
            raise ValueError("No file provided")


class Image(MediaComponent):
    def __str__(self):
        if self.filepath:
            return f"[Image:{self.filepath}]"
        elif self.url:
            return f"[Image:{self.url}]"
        else:
            return f"[Image:{self.base64}]"

    def __repr__(self):
        return f"[Image]"


class Audio(MediaComponent):
    def __str__(self):
        if self.filepath:
            return f"[Audio:{self.filepath}]"
        elif self.url:
            return f"[Audio:{self.url}]"
        else:
            return f"[Audio:{self.base64}]"

    def __repr__(self):
        return f"[Audio]"


class Video(MediaComponent):
    def __str__(self):
        if self.filepath:
            return f"[Video:{self.filepath}]"
        elif self.url:
            return f"[Video:{self.url}]"
        else:
            return f"[Video:{self.base64}]"

    def __repr__(self):
        return f"[Video]"


# TODO: implement classes below
class FileComponent(MessageComponent, ABC):
    pass


class File(FileComponent, ABC):
    pass


class KOOKCardMessage(MessageComponent):

    def __init__(self, content: KOOKCardMsg):
        self.content = content

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "[KOOKCardMessage]"