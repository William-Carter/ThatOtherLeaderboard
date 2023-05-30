import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class RunsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Show Runs", "runs", "List all of a player's runs", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("runner", "The runner whose runs you want to see", cobble.validations.IsString()))
        self.addArgument(cobble.command.Argument("category", "The category of runs you want to see", IsCategory()))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        discordID = dbm.getDiscordIDFromName(argumentValues["runner"])
        if not discordID:
            return f"No runner registered with name '{argumentValues['runner']}'"
        tolID = dbm.getTolAccountID(discordID=discordID)
        runs = dbm.getPlayerRuns(tolID, argumentValues["category"], False, False)
        tableData = [["RunID", "Time"]]
        for run in runs:
            tableData.append([str(run[0]), durations.formatted(run[1])])
        
        output = f"Runs by {argumentValues['runner']}:\n"
        output += "```"+neatTables.generateTable(tableData)+"```"

        return output