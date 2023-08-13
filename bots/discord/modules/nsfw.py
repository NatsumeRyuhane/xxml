from discord.ext import commands

from libs import util
from libs import log


class BasicCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Command()
    async def cmd1(self):
        pass


def setup(client):
    client.add_cog(BasicCommands(client))
