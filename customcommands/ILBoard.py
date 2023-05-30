import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class ILBoardCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "IL Leaderboard", "ilboard", "Show the leaderboard for a given IL", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("map", "The IL map", IsMap()))
        self.addArgument(cobble.command.Argument("category", "The IL category", IsILCategory()))
        self.addArgument(cobble.command.Argument("start", "Where to start from", cobble.validations.IsInteger(), True))
        
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

        if argumentValues["map"] in dbm.levelNames.values():
            argumentValues["map"] = dbm.getMapFromLevelName(argumentValues["map"])

        lbData = dbm.generateILBoard(argumentValues["map"], argumentValues["category"])[start:start+20]
        tableData = [["Place", "Runner", "Time"]]
        for entry in lbData:
            place = durations.formatLeaderBoardPosition(dbm.fetchILPlace(entry[0], argumentValues["category"]))
            runner = entry[1]
            time = entry[2]
            tableData.append([place, runner, time])

        table = "```"+neatTables.generateTable(tableData, padding=2)+"```"

        return table
    