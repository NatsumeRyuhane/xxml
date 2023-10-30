import logging
import argparse
import shlex
import asyncio

import commands
from libs.message import Message
from libs.bot import Bot
from libs.singleton import Singleton

class CommandParser(argparse.ArgumentParser):
    """Custom ArgumentParser that overrides _print_message()"""

    def _print_message(self, message, file = None):
        if message:
            return message


class CommandManager(metaclass = Singleton):
    def __init__(self, command_prefix = '.') -> None:
        self.command_prefix = command_prefix
        self.command_dict = {}
        self.command_alias_dict = {}

    def register_command(self, command_object, command_function):
        # register the command to a dict
        # TODO: Check illegal and duplicate names

        if command_object.command_group != "default":
            logging.info(f"Registering command [{command_object.command_group}] > [{command_object.name}]")
        else:
            logging.info(f"Registering command [{command_object.name}]")

        if command_object.name in self.command_dict.keys():
            raise KeyError(f"Command name \"{command_object.name}\" inflicts with previously registered command")

        self.command_dict[command_object.name] = (command_function, command_object)
        if command_object.aliases:
            for alias in command_object.aliases:
                logging.info(f"Registering command alias [{alias}] for command [{command_object.name}]")

                if alias in self.command_alias_dict.keys():
                    logging.error(f"Registering command alias [{alias}] infliction detected, skipping this alias for command [{command_object.name}]")
                else:
                    self.command_alias_dict[alias] = command_object.name

    def parse_command_from_msg(self, msg: Message) -> str | None:
        try:
            args = shlex.split(msg.get_texts())
            if args and args[0][0] == self.command_prefix:
                if args[0][1:] in self.command_dict.keys():
                    return args[0][1:]
                elif args[0][1:] in self.command_alias_dict.keys():
                    return args[0][1:]

            return None
        except Exception as e:
            return None

    def is_registered_command(self, command: str) -> bool:
        command_signature = command.replace(self.command_prefix, '')

        if command_signature in self.command_dict.keys():
            return True
        else:
            return False

    def is_command_alias(self, alias: str) -> bool:
        command_signature = alias.replace(self.command_prefix, '')

        if command_signature in self.command_alias_dict.keys():
            return True
        else:
            return False

    def get_command_complex(self, command_name: str):
        parsed_command_name = command_name.replace(self.command_prefix, '')

        if self.is_registered_command(parsed_command_name):
            return self.command_dict[parsed_command_name]
        if self.is_command_alias(parsed_command_name):
            return self.command_dict[self.command_alias_dict[parsed_command_name]]
        else:
            return None

    def get_command_function(self, command_name: str) -> callable:
        command_object = self.get_command_complex(command_name)
        if command_object:
            return command_object[0]

    def get_command_object(self, command_name: str):
        command_object = self.get_command_complex(command_name)
        if command_object:
            return command_object[1]

    def run_command(self, bot: Bot, msg: Message):
        """
        parse and run the command in a message as an asyncio task
        """
        command_name = "[UNRESOLVED COMMAND]"
        try:
            command_name = self.parse_command_from_msg(msg)
            if command_name:
                if self.is_command_alias(command_name):
                    logging.info(
                        f"Resolved command alias [{command_name}] to command [{self.command_alias_dict[command_name]}] and running")
                else:
                    logging.info(f"Running command [{command_name}]")

                command_object = self.get_command_object(command_name)
                command_function = self.get_command_function(command_name)

                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(command_function(bot, msg))
                except RuntimeError:
                    asyncio.run(command_function(bot, msg))

        except Exception:
            logging.warning(f"Error running command {command_name}. Traceback:", exc_info = True)


global command_manager
command_manager = CommandManager()


class Command():

    command_manager = command_manager

    def __init__(self, command_name: str, aliases: list[str] = None, command_group = "default",
                 help_short = "") -> None:
        self.name = command_name
        self.aliases = aliases
        self.command_group = command_group
        self.help = help_short

        self.decorated = False


    def __call__(self, command_function):
        def wrapper(*args, **kwargs):
            return command_function(*args, **kwargs)

        if not self.decorated:
            Command.command_manager.register_command(self, wrapper)
            wrapper.__doc__ = command_function.__doc__
            self.decorated = True
        else:
            raise Exception("Attempt to re-decorate a used command object found!")