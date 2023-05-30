import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class CommunityGoldsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Community Golds", "commgolds", "Show the best golds from all the community", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category of your golds", IsCategory()))
    
    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        golds = dbm.getCommgolds(argumentValues["category"])
        golds = sorted(golds, key= lambda x: list(dbm.levelNames.keys()).index(x[1]))

        tableData = [["Level", "Time", "Runner"]]
        for gold in golds:
            tableData.append([dbm.levelNames[gold[1]], str(durations.formatted(gold[2])), gold[0]])

        table = neatTables.generateTable(tableData)
        sob = durations.formatted(sum([x[2] for x in golds]))
        table += "\nCommunity Sum of Best: "+sob

        return f"Commgolds for {argumentValues['category']}:\n```{table}```"