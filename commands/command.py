import logging
import argparse
import shlex
import asyncio

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

        self.commands: dict[str, Command] = {}
        self.command_aliases: dict[str, str] = {}
        self.command_groups: dict[str, list[str]] = {"default": []}

        self.context_actions: dict[str, ContextActions] = {}

    def register_command(self, command_object):
        if command_object.name in self.commands.keys():
            raise KeyError(f"Command name [{command_object.name}] inflicts with previously registered command")

        if command_object.command_group == "default":
            logging.info(f"Registering new command [{command_object.name}]")
        else:
            if command_object.command_group not in self.command_groups.keys():
                logging.info(f"Registering new command group [{command_object.command_group}]")
                self.command_groups[command_object.command_group] = []

            logging.info(f"Registering new command [{command_object.command_group}] > [{command_object.name}]")
            self.command_groups[command_object.command_group].append(command_object.name)

        self.commands[command_object.name] = command_object

        if command_object.aliases:
            for alias in command_object.aliases:
                logging.info(f"Registering command alias [{alias}] for command [{command_object.name}]")

                if alias in self.command_aliases.keys():
                    logging.error(f"Registering command alias [{alias}] inflicts with previously registered alias, skipping this alias for command [{command_object.name}]")
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
                        f"Resolved command alias [{command_name}] to command [{self.command_aliases[command_name]}] and running")
                else:
                    logging.info(f"Running command [{command_name}]")

                command_object = self.get_command_object(command_name)
                command_function = command_object.function

                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(command_object.function(bot, msg))
                except RuntimeError:
                    asyncio.run(command_object.function(bot, msg))

        except Exception as e:
            logging.warning(f"Error running command {command_name}: \n{e}")


command_manager = CommandManager()


class Command():
    command_manager = command_manager

    def __init__(self, command_name: str, aliases: list[str] = None, command_group = "default",
                 help = "", short_help = "") -> None:
        self.name = command_name
        self.aliases = aliases
        self.command_group = command_group
        self.short_help = short_help
        self.help = help
        self.function = None

        self.decorated = False

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


class ContextActions:

    def __init__(self):
        self.actions: dict[str, callable] = {}

    def add_action(self, action_name: str = "", action_callback: callable = None):
        pass

    def run_action(self, action_name: str = "", action_callback: callable = None):
        pass

    def onInterrupt(self):
        pass
