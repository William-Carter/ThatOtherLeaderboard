import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class SumOfILsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Sum of ILs", "soils", "Show your sums of ILs", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("tol", "The tol username of the user you want the sum of ILs of", cobble.validations.IsString(), True))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        if len(argumentValues.keys()) == 0:
            runnerID = dbm.getTolAccountID(discordID=messageObject.author.id)
            runnerName = messageObject.author.name

        elif "tol" in argumentValues.keys():
            runnerID = dbm.getTolIDFromName(argumentValues["tol"])
            runnerName = argumentValues["tol"]

        tableRows = {"glitchless": "Glitchless Std.",
                "glitchlessAdv": "Glitchless Full",
                "inbounds": "Inbounds Std.",
                "inboundsAdv": "Inbounds Full",
                "oob": "Out of Bounds Std.",
                "oobAdv": "Out of Bounds Full"}
        soils = {"glitchless": 0,
                "glitchlessAdv": 0,
                "inbounds": 0,
                "inboundsAdv": 0,
                "oob": 0,
                "oobAdv": 0}
        
        pbs = dbm.getRunnerILPBs(runnerID)
        

        for pb in pbs:
            soils[pb[2]+"Adv"] += pb[3]
            if not "advanced" in pb[1]:
                soils[pb[2]] += pb[3]

        tableData = [["Category", "Sum"]]
        for soil in soils.keys():
            tableData.append([tableRows[soil], durations.formatted(soils[soil])])

        table = neatTables.generateTable(tableData)
        table = "```\n"+table+"```"
        return table