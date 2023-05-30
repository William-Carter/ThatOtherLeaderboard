import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

class DeleteRunCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Delete run", "delete", "Delete the specified run", cobble.permissions.ADMIN)
        self.addArgument(cobble.command.Argument("runID", "The ID of the run you want to delete", cobble.validations.IsInteger()))
        self.postCommand = lambda: dbm.updateLeaderboardLight()


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        dbm.deleteRun(int(argumentValues["runID"]))
        return "Run deleted"