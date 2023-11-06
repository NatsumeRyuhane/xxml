import logging
import argparse
import shlex
import asyncio
import typing
from enum import Enum

from libs.message import Message
from libs.bot import Bot
from libs.singleton import Singleton


class ContextActions:
    class ContextActionType(Enum):
        ON_COMMAND = 1
        ON_NEXT_MESSAGE = 2
        ON_NEXT_EVENT = 4

    def __init__(self, action_type: ContextActionType = ContextActionType.ON_COMMAND, command_prefix: str = ""):
        self.action_type = action_type
        self.command_prefix = command_prefix
        self.actions: dict[str, typing.Coroutine] = {}

    def add_action(self, action_name: str = ""):
        if self.action_type == ContextActions.ContextActionType.ON_COMMAND:
            def decorator(function: typing.Coroutine):
                self.actions[action_name] = function

            return decorator
        else:
            # For event-triggered context actions, the only key in self.actions is defined as "action"
            def decorator(function: typing.Coroutine):
                self.actions["action"] = function

            return decorator

    def parse_action_from_msg(self, msg: Message) -> str | None:
        try:
            args = shlex.split(msg.get_texts())
            if args and args[0][0] == self.command_prefix:
                if args[0][1:] in self.actions.keys():
                    return args[0][1:]

            return None
        except Exception as e:
            logging.error(e)
            return None

    def run_action(self, action_name: str, bot: Bot, msg: Message):
        action = self.actions[action_name]

        logging.info(f"Running context action [{action_name}]")

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(action(bot, msg))
        except RuntimeError:
            asyncio.run(action(bot, msg))

    def on_interrupt(self):
        pass


class CommandParser(argparse.ArgumentParser):
    """Custom ArgumentParser that overrides _print_message()"""

    def _print_message(self, message, file = None) -> typing.Any:
        if message:
            return message


class CommandManager(metaclass = Singleton):
    def __init__(self, command_prefix = '.') -> None:
        self.command_prefix = command_prefix

        self.commands: dict[str, Command] = {}
        self.command_aliases: dict[str, str] = {}
        self.command_groups: dict[str, list[str]] = {"default": []}

        self.context_actions: dict[str, ContextActions] = {}

    def register_command(self, command_object) -> None:
        if command_object.name in self.commands.keys():
            raise KeyError(f"Command name [{command_object.name}] inflicts with previously registered command")
        else:
            if command_object.command_group not in self.command_groups.keys():
                logging.info(f"Registering new command group [{command_object.command_group}]")
                self.command_groups[command_object.command_group] = []

            if command_object.command_group == "default":
                logging.info(f"Registering new command [{command_object.name}]")
            else:
                logging.info(f"Registering new command [{command_object.command_group}] > [{command_object.name}]")
            self.command_groups[command_object.command_group].append(command_object.name)

        self.commands[command_object.name] = command_object

        if command_object.aliases:
            for alias in command_object.aliases:
                logging.info(f"Registering command alias [{alias}] for command [{command_object.name}]")

                if alias in self.command_aliases.keys():
                    logging.error(f"Command alias [{alias}] inflicts with previously registered alias, skipping this alias for command [{command_object.name}]")
                else:
                    self.command_aliases[alias] = command_object.name

    def parse_command_from_msg(self, msg: Message) -> str | None:
        try:
            args = shlex.split(msg.get_texts())
            if args and args[0][0] == self.command_prefix:
                if args[0][1:] in self.commands.keys():
                    return args[0][1:]
                elif args[0][1:] in self.command_aliases.keys():
                    return args[0][1:]

            return None
        except Exception as e:
            logging.error(e)
            return None

    def is_registered_command(self, command: str) -> bool:
        command_name = command.replace(self.command_prefix, '')

        if command_name in self.commands.keys():
            return True
        else:
            return False

    def is_command_alias(self, alias: str) -> bool:
        command_alias = alias.replace(self.command_prefix, '')

        if command_alias in self.command_aliases.keys():
            return True
        else:
            return False

    def get_command_object(self, command_name: str):
        parsed_command_name = command_name.replace(self.command_prefix, '')

        if self.is_registered_command(parsed_command_name):
            return self.commands[parsed_command_name]
        if self.is_command_alias(parsed_command_name):
            return self.commands[self.command_aliases[parsed_command_name]]
        else:
            return None

    def set_context_actions(self, msg: Message, action_type = ContextActions.ContextActionType.ON_COMMAND):
        new_context_actions = ContextActions(action_type, self.command_prefix)
        self.context_actions[msg.context.sender_id] = new_context_actions

        return new_context_actions

    def clear_context_action(self, msg: Message):
        if msg.context.sender_id in self.context_actions.keys():
            del self.context_actions[msg.context.sender_id]

    def run_context_action(self, bot: Bot, msg: Message) -> bool:
        if msg.context.sender_id in self.context_actions.keys():
            context_action = self.context_actions[msg.context.sender_id]

            if context_action:
                if context_action.action_type == ContextActions.ContextActionType.ON_COMMAND:
                    action_name = context_action.parse_action_from_msg(msg)
                    context_action.run_action(action_name, bot, msg)
                    return True
                else:
                    context_action.run_action("action", bot, msg)
                    return True

        return False

    def run_command(self, bot: Bot, msg: Message):
        command_name = "[UNRESOLVED COMMAND]"
        try:
            command_name = self.parse_command_from_msg(msg)
            if command_name:
                if self.is_command_alias(command_name):
                    logging.info(
                        f"Resolved command alias [{command_name}] to command [{self.command_aliases[command_name]}] and running")
                else:
                    logging.info(f"Running command [{command_name}]")

                # the prev context actions will be cleared on successfully resolving a command
                self.clear_context_action(msg)
                command_object = self.get_command_object(command_name)

                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(command_object.function(bot, msg))
                except RuntimeError:
                    asyncio.run(command_object.function(bot, msg))

        except Exception as e:
            logging.warning(f"Error running command {command_name}: \n{e}")


command_manager = CommandManager()


class Command:
    command_manager = command_manager

    def __init__(self, command_name: str, aliases: list[str] = None, command_group = "default",
                 help = "", short_help = "") -> None:
        self.name: str = command_name
        self.aliases: list[str] = aliases
        self.command_group: str = command_group
        self.short_help: str = short_help
        self.help: str = help
        self.function: typing.Union[typing.Coroutine, None] = None

        self.decorated: bool = False

    def __call__(self, command_function):
        if not self.decorated:
            Command.command_manager.register_command(self)
            if self.help == "":
                self.help = command_function.__doc__
            self.decorated = True
            self.function = command_function
        else:
            pass
            # maybe just do nothing is fine here?
            # raise Exception("Attempt to re-decorate a used command object found!")
