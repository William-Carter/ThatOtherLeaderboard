import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class AverageRankBoardCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Average Rank Leaderboard", "arboard", "Show the leaderboard for average ranks", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("start", "What place to start from", cobble.validations.IsInteger(), True))
        self.addArgument(cobble.command.Argument("useCache", "Whether to use the stored values or recalculate them", cobble.validations.IsBool(), True))
        

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        if not "start" in argumentValues:
            argumentValues["start"] = 1

        argumentValues["start"] = int(argumentValues["start"])

        useCache = True
        if "useCache" in argumentValues:
            if argumentValues["useCache"] == "false":
                useCache = False
                
        averageRanks = dbm.getAverageRankLeaderboard(useCache)[argumentValues["start"]-1:argumentValues["start"]+19]
        
        tableData = [["Place", "Runner", "Average Rank"]]
        for index, entry in enumerate(averageRanks):
            tableData.append([str(index+argumentValues["start"]
                                  )+".", entry[0], str(entry[1])])

        table = "```"+neatTables.generateTable(tableData, padding=2)+"```"
        return table