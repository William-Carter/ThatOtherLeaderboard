import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class GoldsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Show Golds", "golds", "Show your golds for a given category", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category of your golds", IsCategory()))
        self.addArgument(cobble.command.Argument("tol", "The tol username of the user you want the profile of", cobble.validations.IsString(), True))
    
    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        if "tol" in argumentValues.keys():
            runnerName = argumentValues["tol"]
            tolID = dbm.getTolIDFromName(argumentValues["tol"])
            if not tolID:
                return f"No registered player with name {argumentValues['tol']}"
        else:
            tolID = dbm.getTolAccountID(discordID=messageObject.author.id)
            runnerName = dbm.getNameFromTolID(tolID)
        golds = dbm.grabGolds(tolID, argumentValues["category"])
        golds = sorted(golds, key= lambda x: list(dbm.levelNames.keys()).index(x[0]))
        if len(golds) == 0:
            return "User has no saved golds!"

        

        tableData = [["Level", "Time"]]
        for gold in golds:
            tableData.append([dbm.levelNames[gold[0]], str(durations.formatted(gold[1]))])

        table = neatTables.generateTable(tableData)
        sob = durations.formatted(sum([x[1] for x in golds]))
        table += "\nSum of Best: "+sob

        return f"{runnerName}'s {argumentValues['category']} golds:\n```{table}```"