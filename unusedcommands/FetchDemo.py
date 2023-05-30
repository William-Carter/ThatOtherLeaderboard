import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

class FetchDemoCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Fetch IL Demo", "fetchdemo", "Retrieve the demo for an IL", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("category", "The category of the demo", IsILCategory()))
        self.addArgument(cobble.command.Argument("level", "The category of your golds", IsMap()))
        self.addArgument(cobble.command.Argument("user", "The person whose demo you want", cobble.validations.IsString(), True))
