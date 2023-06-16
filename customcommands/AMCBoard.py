import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class AMCBoardCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "All Main Categories Leaderboard", ["amcboard", "amcb"], "Show the leaderboard for the sum of a person's PBs", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("start", "What place to start from", cobble.validations.IsInteger(), True))
        
        

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        if not "start" in argumentValues:
            argumentValues["start"] = 1

        argumentValues["start"] = int(argumentValues["start"])

        amcBoard = dbm.generateAMCBoard()[argumentValues["start"]-1:argumentValues["start"]+19]

        tableData = [["Place", "Runner", "AMC Estimate"]]
        for index, entry in enumerate(amcBoard):
            tableData.append([
                str(index+argumentValues["start"])+".", 
                entry["name"], 
                durations.formatted(entry["time"])
                ])
            
        table = "```"+neatTables.generateTable(tableData, padding=2)+"```"
        return table