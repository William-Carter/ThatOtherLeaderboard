import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class ILWRsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "IL WRs", "ilwrs", "Show the current IL world records", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("category", "The category to see WRs for", IsILCategory()))
        


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        category = argumentValues["category"]

        forCats = ["glitchless", "inbounds", "oob"]
        wrs = dbm.getILWRs()
        tableData = [["Level", "Time", "Runner"]]
        for level in dbm.levelNames.keys():
            row = [dbm.levelNames[level]]

            relevantPB = ""
            fastestValidRun = []
            for wr in wrs:
                if wr[1] == level and forCats.index(wr[2]) <= forCats.index(category):
                    if len(fastestValidRun) != 0:
                        if wr[3] < fastestValidRun[3]:
                            fastestValidRun = wr
                    else:
                        fastestValidRun = wr
            if len(fastestValidRun) != 0:
                wrTime = fastestValidRun[3]
                runnerName = fastestValidRun[4]
                relevantPB = f"{durations.formatted(wrTime)}"
                            

                row.append(relevantPB)
                row.append(runnerName)
                

            tableData.append(row)

        table = neatTables.generateTable(tableData)
        
        
        table = ["Current IL World Records"] + [neatTables.codeBlock(table[:1990])]
        
        
        
        return table