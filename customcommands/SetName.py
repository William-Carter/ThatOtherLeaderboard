import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

class SetNameCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Set Name", "setname", "Set your name on TOL", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("name", "The value you want to set your name to", IsNormal()))

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        tolAccount = dbm.getTolAccountID(discordID = messageObject.author.id)
        if dbm.getTolIDFromName(argumentValues["name"]):
            return "This name is already in use"
        dbm.updateTolName(tolAccount, argumentValues["name"])
        return "Account name updated"