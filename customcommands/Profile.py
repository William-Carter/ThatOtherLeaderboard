import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import durations
import neatTables

class ProfileCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """

        super().__init__(bot, "Profile", ["profile", "pf"], "Show your profile, including all your personal bests", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("tol", "The tol username of the user you want the profile of", cobble.validations.IsString(), True))
        self.addArgument(cobble.command.Argument("srcom", "The srcom username of the user you want the profile of", cobble.validations.IsString(), True))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict):
        """
        Generate a profile for the given player (or the sender, if no player is provided)
        Parameters:
            messageObject - the object corresponding to the message that triggered the command
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        Returns:
            output - A table displaying the leaderboard
        """
        if len(argumentValues.keys()) > 1:
            return "Can only return a profile for either a speedrun.com account or a TOL account, not both!"
        
        if len(argumentValues.keys()) == 0:
            runnerID = dbm.getTolAccountID(discordID=messageObject.author.id)
            runnerName = dbm.getNameFromTolID(runnerID)
            mode = "tol"

        elif "tol" in argumentValues.keys():
            runnerID = dbm.getTolIDFromName(argumentValues["tol"].lower())
            runnerName = argumentValues["tol"]
            mode = "tol"

        elif "srcom" in argumentValues.keys():
            runnerID = dbm.getSrcomIDFromSrcomName(argumentValues["srcom"])
            runnerName = argumentValues["srcom"]
            mode = "srcom"

        tableData = [["Category", "Time", "Place"]]

        forCats = {"oob": "OoB", "inbounds": "Inbounds", "unrestricted": "NoSLA Unr.", "legacy": "NoSLA Leg.", "glitchless": "Glitchless"}
        totalPlaces = 0
        amcTime = 0
        catsUsed = 0
        for category in forCats.keys():
            if mode == "tol":
                runs = dbm.getPlayerRuns(runnerID, category)
            elif mode == "srcom":
                runs = dbm.getPlayerRuns("", category, srcomID=runnerID)

            if len(runs) > 0:
                
                sortedRuns = sorted(runs, key=lambda x: x[1])
                tableCat = forCats[category]
                runTime = sortedRuns[0][1]
                if category != "unrestricted":
                    catsUsed += 1
                    amcTime += runTime
                tableTime = durations.formatted(runTime)
                place = dbm.fetchLeaderboardPlace(sortedRuns[0][0], category)
                tablePlace = durations.formatLeaderBoardPosition(place)
                totalPlaces += place

                tableData.append([tableCat, tableTime, tablePlace])

        if catsUsed == 4:
            tableData.append(["", "", ""])
            tableData.append(["AMC Estimate", durations.formatted(amcTime), ""])

        if len(tableData) < 2:
            return "No runs found!"
        output = f"Profile for {runnerName}:\n"
        output += "```"+neatTables.generateTable(tableData)
        if mode == "tol":
            averageRank = dbm.getAverageRank(runnerID)[0]

        elif mode == "srcom":
            averageRank = dbm.getAverageRank("", srcomAccount=runnerID)[0]
        output += f"Average Placement: {averageRank}"+"```"
        return output