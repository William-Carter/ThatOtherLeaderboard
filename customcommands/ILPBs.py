import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class ILPBsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "IL PBs", "ilpbs", "Show your IL pbs", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("tol", "The tol username of the user you want the profile of", cobble.validations.IsString(), True))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        if len(argumentValues.keys()) == 0:
            runnerID = dbm.getTolAccountID(discordID=messageObject.author.id)
            runnerName = messageObject.author.name

        elif "tol" in argumentValues.keys():
            runnerID = dbm.getTolIDFromName(argumentValues["tol"])
            runnerName = argumentValues["tol"]




        forCats = ["glitchless", "inbounds", "oob"]
        pbs = dbm.getRunnerILPBs(runnerID)
        tableData = [["Level", "Glitchless", "Inbounds", "Out of Bounds"]]
        for level in dbm.levelNames.keys():
            row = [dbm.levelNames[level]]
            for category in  forCats:
                relevantPB = ""
                fastestValidRun = []
                for pb in pbs:
                    if pb[1] == level and forCats.index(pb[2]) <= forCats.index(category):
                        if len(fastestValidRun) != 0:
                            if pb[3] < fastestValidRun[3]:
                                fastestValidRun = pb
                        else:
                            fastestValidRun = pb
                if len(fastestValidRun) != 0:
                    place = dbm.fetchILPlace(fastestValidRun[0])
                    pbTime = fastestValidRun[3]
                    relevantPB = f"{durations.formatted(pbTime)}, {durations.formatLeaderBoardPosition(place)}"
                            

                row.append(relevantPB)

            tableData.append(row)

        table = neatTables.generateTable(tableData)
        table = "```\n"+table+"```"
        output = f"IL PBs for {runnerName}:\n"+table
        return output