import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

class CommunityGoldEligibilityCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Set Commgold Eligibilty", "eligible", "Toggle whether your gold for a given level should be considered when finding commgolds.", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category of your gold", IsCategory()))
        self.addArgument(cobble.command.Argument("level", "The level to update", IsMap()))
    
    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        tolID = dbm.getTolAccountID(discordID=messageObject.author.id)

        if argumentValues["level"] in dbm.levelNames.values():
            argumentValues["level"] = dbm.getMapFromLevelName(argumentValues["level"])

        currentEligiblity = dbm.getComgoldEligibility(tolID, argumentValues["category"], argumentValues["level"])
        if not currentEligiblity:
            return "User does not have this gold!"
        currentEligiblity = currentEligiblity[0]
        print(currentEligiblity)

        response = f"Your gold for {dbm.levelNames[argumentValues['level']]} is "
        if currentEligiblity == "yes":
            newEligibility = "no"
            response += "no longer eligible for commgold"
        else:
            newEligibility = "yes"
            response += "now eligible for commgold"

        dbm.updateComgoldEligibility(newEligibility, tolID, argumentValues["category"], argumentValues["level"])

        return response