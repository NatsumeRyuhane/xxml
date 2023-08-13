import os
import traceback

import discord
from discord.ext import commands

import libs.log as logging
import libs.util as util

from main import client, config, internal_ID


def load_all_extensions():
    succeeded_extensions = []
    failed_extensions = []
    for extensions in os.listdir('libs'):
        if extensions.endswith('.py'):
            try:
                client.load_extension(f'libs.{extensions[:-3]}')
                succeeded_extensions.append(extensions[10:-3])
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                pass
            except Exception:
                failed_extensions.append(extensions[10:-3])
    return [succeeded_extensions, failed_extensions]


def unload_all_extensions():
    succeeded_extensions = []
    failed_extensions = []
    for extensions in os.listdir('libs'):
        if extensions.endswith('.py'):
            try:
                client.unload_extension(f'libs.{(extensions[:-3])}')
                succeeded_extensions.append(extensions[10:-3])
            except discord.ext.commands.errors.ExtensionNotLoaded:
                pass
            except Exception:
                failed_extensions.append(extensions[10:-3])
    return [succeeded_extensions, failed_extensions]


async def load_extension(context, extension_name):
    if extension_name == "all":
        load_all_extensions()
    else:
        try:
            client.load_extension(f'libs.{extension_name}')
            await logging.info(f"Extension `{extension_name}` loaded successfully", None, 'load_extension', None,
                               extension_name,
                               str(context.message.author))
            await context.send(f"好~嘞，加载好插件`{extension_name}`啦！", file = util.reaction(5))

        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            await logging.warning(f"Extension `{extension_name}` was already loaded", None, 'load_extension', None,
                                  extension_name, str(context.message.author))
            await context.send(f"插件`{extension_name}`运行的好好的！重启插件去用`.reload [extensionName]`好吗！", file = util.reaction(3))

        except discord.ext.commands.errors.ExtensionNotFound:
            await logging.warning(f"Unable to find extension `{extension_name}`", None, 'load_extension', None,
                                  extension_name,
                                  str(context.message.author))
            await context.send(f"找不到你说的那个什么鬼插件`{extension_name}`啊...你这拼法是和犽犽学的？", file = util.reaction(3))

        except Exception:
            await logging.error(f"Failed to load extension `{extension_name}`", traceback.format_exc(),
                                'load_extension', None,
                                extension_name, str(context.message.author))
            await context.send(f"加载插件`{extension_name}`的时候出错了！可能这个插件坏掉了吧...", file = util.reaction(6))


async def unload_extension(context, extension_name):
    if extension_name == "all":
        unload_all_extensions()
    else:
        try:
            client.unload_extension(f'libs.{extension_name}')
            await logging.info("Unloaded extension by the command of %s" % str(context.message.author))
            await context.send(f"欸？插件`{extension_name}`这就不要了？", file = util.reaction(1))
            await logging.info(f"Extension `{extension_name}` unloaded successfully", None, 'unload_extension', None,
                               extension_name, str(context.message.author))

        except discord.ext.commands.errors.ExtensionNotLoaded:
            await logging.warning(f"Target extension `{extension_name}` was not running", None, 'unload_extension',
                                  None,
                                  extension_name, str(context.message.author))
            await context.send(f"我这里没有在运行你说的那个什么`{extension_name}`啊？你拼写错了？都跟你说了这个不要跟犽犽学...", file = util.reaction(4))

        except Exception:
            await logging.error(f"Failed to unload extension `{extension_name}`", traceback.format_exc(),
                                'unload_extension',
                                None, extension_name, str(context.message.author))
            await context.send(f"卸载插件`{extension_name}`的时候好像有什么出错了！具体是什么问题你自己去日志找traceback看吧...", file = util.reaction(6))


async def privilege_check(context):
    app_info = await client.application_info()
    if app_info.owner == context.message.author:
        return True
    else:
        return False


# Events

# This event triggers when bot is connected to discord's server
@client.event
async def on_ready():
    await logging.info(message = f"Bot client started/reconnected successfully, internal_ID = {internal_ID}")
    if config['settings']['debug_mode'] is False:
        for servers in client.guilds:
            try:
                restart_messages = []
                await servers.system_channel.send(util.append_random_string(restart_messages))
            except Exception:
                await logging.warning(f"Restart message sending failed on server {servers.name}(ID = {servers.id})",
                                      traceback.format_exc())


# Core Commands

@client.Command()
async def _id(context):
    await  context.send(f"小毛龙在尾巴尖的毛里面发现了这个！\n`> {internal_ID} <`\n...这个是干什么用的？", file = util.reaction("HTTP/400_alt"))
    await logging.info(command_executed = '_id', user = str(context.message.author))


# This command is used to stop the program via discord chat so that I don't need to ps -ef and find PID of this program
@client.Command(aliases = ['kill'])
async def terminal(context, target_ID = 0):
    if internal_ID == target_ID:
        if await privilege_check(context):
            if config['settings']['debug_mode'] is False:
                for servers in client.guilds:
                    try:
                        terminate_messages = []
                        await servers.system_channel.send(util.append_random_string(terminate_messages), file = util.reaction(2))
                    except Exception:
                        await logging.warning(f"Terminal message sending failed on server {servers.name}(ID = {servers.id})",
                                              traceback.format_exc())
            await logging.info("Bot terminated", None, 'terminal', None, None, str(context.message.author))
            exit(0)
        else:
            await context.send("才不要！能命令小毛龙的只有小毛龙~", file = util.reaction(7))
            await logging.warning("Execution aborted due to insufficient privilege", None, 'terminal', None, None,
                                  str(context.message.author))
    await logging.warning(f"Execution aborted due to unmatched internal_ID, self internal_ID = {internal_ID}",
                          command_executed = 'terminal', inputs = target_ID, user = str(context.message.author))


@client.Command()
async def load(context, extension_name):
    if await privilege_check(context):
        await load_extension(context, extension_name)
    else:
        await context.send("才不要！能命令小毛龙的只有小毛龙~", file = util.reaction(7))
        await logging.warning("Execution aborted due to insufficient privilege", None, 'load', None, extension_name,
                              str(context.message.author))


@client.Command()
async def unload(context, extension_name):
    if privilege_check(context):
        await unload_extension(context, extension_name)
    else:
        await context.send("才不要！能命令小毛龙的只有小毛龙~", file = util.reaction(7))
        await logging.warning("Execution aborted due to insufficient privilege", None, 'unload', None, extension_name,
                              str(context.message.author))


@client.Command
async def reload(context, extension_name):
    if privilege_check(context):
        await unload_extension(context, extension_name)
        await load_extension(context, extension_name)

    else:
        await context.send("才不要！能命令小毛龙的只有小毛龙~")
        await logging.warning("Execution aborted due to insufficient privilege", None, 'reload', None, extension_name,
                              str(context.message.author))

client.run(config['token'])
