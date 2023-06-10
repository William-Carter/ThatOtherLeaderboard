import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class CompareCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Compare", "compare", "Compare yourself with another player, or other players against each other", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("type", "What to compare", IsComparisonType()))
        self.addArgument(cobble.command.Argument("runner 1", "The tol username of the user you want to comapre to", cobble.validations.IsString()))
        self.addArgument(cobble.command.Argument("runner 2", "The tol username of the runner to compare against the first runner", cobble.validations.IsString(), True))



    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        
        if "runner 2" in argumentValues.keys():
            runner1ID = dbm.getTolIDFromName(argumentValues["runner 1"])
            runner2ID = dbm.getTolIDFromName(argumentValues["runner 2"])
            if not runner1ID:
                return f"No registered runner with name {argumentValues['runner 1']}"
            if not runner2ID:
                return f"No registered runner with name {argumentValues['runner 2']}"
        else:
            runner1ID = dbm.getTolAccountID(messageObject.author.id)
            runner2ID = dbm.getTolIDFromName(argumentValues["runner 1"]) # Kinda confusing but it makes it easy to do both use cases with the same code

        if not runner2ID:
                return f"No registered runner with name {argumentValues['runner 1']}"

        runners = [runner1ID, runner2ID]
        
        
        match argumentValues["type"]:
             case "ranks":
                # The empty cells are for places
                tableData = [["Category", "OoB", "Inbounds", "NoSLA Unr.", "NoSLA Leg.", "Glitchless","", "Average Rank"]]
                for runner in runners:
                    runnerName = dbm.getNameFromTolID(runner)
                    runnerResults = [runnerName]
                    forCats = {"oob": "OoB", "inbounds": "Inbounds", "unrestricted": "NoSLA Unr.", "legacy": "NoSLA Leg.", "glitchless": "Glitchless"}
                    for category in forCats.keys():
                        runs = dbm.getPlayerRuns(runner, category)
                        if len(runs) > 0:
                            sortedRuns = sorted(runs, key=lambda x: x[1])
                            tableTime = durations.formatted(sortedRuns[0][1])
                            place = dbm.fetchLeaderboardPlace(sortedRuns[0][0], category)
                            tablePlace = durations.formatLeaderBoardPosition(place)
                            runnerResults += [tableTime + ", " + tablePlace]
                    runnerResults.append("")
                    runnerResults.append(str(dbm.getAverageRank(runner)[0]))
                    tableData.append(runnerResults)

                tableData = [list(reversed(x)) for x in list(zip(*tableData[::-1]))]
                table = neatTables.generateTable(tableData)
                table = neatTables.codeBlock(table)
                return table



