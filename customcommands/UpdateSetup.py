import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

class UpdateSetupCommand(cobble.command.Command):

    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Update Setup", "updatesetup", "Update your setup", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("element", "The part of your setup you want to update", IsSetupElement()))
        self.addArgument(cobble.command.Argument("value", "The value to fill for the specified element", IsNormal()))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Show the recorded setup for a given player
        Parameters:
            messageObject - the object corresponding to the message that triggered the command
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        Returns:
            response - A string response containing a list of the player's setup elements
        """
        element = argumentValues["element"]
        value = argumentValues["value"]

        match element:
            case "dpi":
                if not cobble.validations.IsInteger.validate("", value):
                    return "DPI must be a valid integer!"
                if not cobble.validations.IsPositive.validate("", value):
                    return "DPI must be positive!"
                
            case "sensitivity":
                if not cobble.validations.IsNumber.validate("", value):
                    return "Sensitivity must be a number!"
                if not cobble.validations.IsPositive.validate("", value):
                    return "Sensitivity must be positive!"
                
            case "hz":
                if not cobble.validations.IsNumber.validate("", value):
                    return "Refresh rate must be a number!"
                if not cobble.validations.IsPositive.validate("", value):
                    return "Refresh rate must be positive!"
                    
            case _:
                pass
                
        tolID = dbm.getTolAccountID(discordID=messageObject.author.id)
        dbm.insertOrUpdateSetupElement(tolID, element, value)
        return "Setup successfully updated."