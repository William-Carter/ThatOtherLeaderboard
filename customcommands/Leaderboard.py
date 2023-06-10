import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables



class LeaderboardCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Leaderboard", ["leaderboard", "lb"], "Show the leaderboard for a category", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("category", "The category you wish to see the leaderboard for", IsCategory()))
        self.addArgument(cobble.command.Argument("start", "What place to start from", cobble.validations.IsInteger(), True))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        if "start" in argumentValues.keys():
            start = int(argumentValues["start"])-1
        else:
            start = 0
        lbData = dbm.generateLeaderboard(argumentValues["category"])[start:start+20]
        tableData = [["Place", "Runner", "Time"]]
        for entry in lbData:
            tableData.append([str(entry[2])+".", entry[0], entry[1]])

        table = "```"+neatTables.generateTable(tableData, padding=2)+"```"

        return table
