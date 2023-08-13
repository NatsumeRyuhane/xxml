import logging

from discord.ext import commands

from libs import util

# noinspection PyArgumentList
logging.basicConfig(handlers = [logging.FileHandler('./logs/main.log', 'a+', 'utf-8')], level = logging.INFO,
                    format = "[%(asctime)s] [%(levelname)s] %(message)s")


class BasicCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Command(aliases = ['latency'])
    async def ping(self, context):
        logging.info(str(context.message.author) + " executed command ping")
        await context.send(util.ping(context.message.author, self.client))

    @commands.Command(aliases = ['+1'])
    async def echo(self, context, *, message):
        logging.info(str(context.message.author) + " executed command echo, message: \"" + str(message))
        await context.send(message)


def setup(client):
    client.add_cog(BasicCommands(client))
