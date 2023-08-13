import logging
import os
import libs.util
from main import client, config

if not os.path.exists("./logs"):
    os.makedirs("./logs")

# noinspection PyArgumentList
logging.basicConfig(
    handlers = [logging.FileHandler(f'./logs/{config["logging_configurations"]["main_log_filename"]}', 'a+', 'utf-8')],
    level = logging.INFO, format = "[%(asctime)s] [%(levelname)s] %(message)s\n")


def generate_log_message__local(message = None, traceback_message = None, command_executed = None, outputs = None,
                                inputs = None, user = None):
    log_message = ""
    if message is not None: log_message += f"\n{message}"
    if traceback_message is not None: log_message += f"\n[Traceback]\n{traceback_message}"
    if command_executed is not None: log_message += f"\n[Command] {command_executed}"
    if inputs is not None: log_message += f"\n[Inputs] {str(inputs)}"
    if outputs is not None: log_message += f"\n[Outputs]\n {outputs}"
    if user is not None: log_message += f"\n[User] {user}"
    return log_message


def generate_log_messasge__remote(message = None, traceback_message = None, command_executed = None, outputs = None,
                                  inputs = None, user = None, level = "INFO"):
    log_message = f"**[{level}]**\n"
    log_message += "```"
    if message is not None: log_message += f"\n{message}\n"
    if traceback_message is not None: log_message += f"\n[Traceback]\n \n{traceback_message}\n"
    if command_executed is not None: log_message += f"\n[Command] {command_executed}\n"
    if inputs is not None: log_message += f"\n[Inputs] {str(inputs)}\n"
    if outputs is not None: log_message += f"\n[Outputs]\n {outputs}\n"
    if user is not None: log_message += f"\n[User] {user}\n"
    log_message += "```"
    return log_message


async def info(message = None, traceback_message = None, command_executed = None, outputs = None, inputs = None, user = None):
    if config['logging_configurations']['save_local_logs']:
        logging.info(generate_log_message__local(message, traceback_message, command_executed, outputs, inputs, user))
    if config['logging_configurations']['send_logs_to_channel']:
        await client.get_channel(config['logging_configurations']['remote_log_channel_id']).send(
            generate_log_messasge__remote(message, traceback_message, command_executed, outputs, inputs, user, "INFO"))


async def warning(message = None, traceback_message = None, command_executed = None, outputs = None, inputs = None, user = None):
    if config['logging_configurations']['save_local_logs']:
        logging.warning(generate_log_message__local(message, traceback_message, command_executed, outputs, inputs, user))
    if config['logging_configurations']['send_logs_to_channel']:
        await client.get_channel(config['logging_configurations']['remote_log_channel_id']).send(
            generate_log_messasge__remote(message, traceback_message, command_executed, outputs, inputs, user, "WARNING"))


async def error(message = None, traceback_message = None, command_executed = None, outputs = None, inputs = None, user = None):
    if config['logging_configurations']['save_local_logs']:
        logging.error(generate_log_message__local(message, traceback_message, command_executed, outputs, inputs, user))
    if config['logging_configurations']['send_logs_to_channel']:
        await client.get_channel(config['logging_configurations']['remote_log_channel_id']).send(
            generate_log_messasge__remote(message, traceback_message, command_executed, outputs, inputs, user, "ERROR"))


async def critical(message = None, traceback_message = None, command_executed = None, outputs = None, inputs = None, user = None):
    if config['logging_configurations']['save_local_logs']:
        logging.critical(generate_log_message__local(message, traceback_message, command_executed, outputs, inputs, user))
    if config['logging_configurations']['send_logs_to_channel']:
        await client.get_channel(config['logging_configurations']['remote_log_channel_id']).send(
            generate_log_messasge__remote(message, traceback_message, command_executed, outputs, inputs, user, "CRITICAL"))


async def fatal(message = None, traceback_message = None, command_executed = None, outputs = None, inputs = None, user = None):
    if config['logging_configurations']['save_local_logs']:
        logging.fatal(generate_log_message__local(message, traceback_message, command_executed, outputs, inputs, user))
    if config['logging_configurations']['send_logs_to_channel']:
        await client.get_channel(config['logging_configurations']['remote_log_channel_id']).send(
            generate_log_messasge__remote(message, traceback_message, command_executed, outputs, inputs, user, "FATAL"))
