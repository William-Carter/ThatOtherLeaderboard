import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import datetime

class BehalfCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Submit on Behalf", "behalf", "Submit a run to the leaderboard on behalf of another user", cobble.permissions.ADMIN)
        self.addArgument(cobble.command.Argument("runner", "The runner who performed the run", cobble.validations.IsString()))
        self.addArgument(cobble.command.Argument("category", "The category of the run", IsCategory()))
        self.addArgument(cobble.command.Argument("time", "The duration of the run", IsDuration()))

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        time =  round(round((durations.seconds(argumentValues["time"])/0.015), 0)*0.015, 3) # Convert entered time to seconds and correct to the nearest tick value
        
        runnerID = dbm.getTolIDFromName(argumentValues["runner"])
        if not runnerID:
            return f"No registered user with name '{argumentValues['runner']}'"
        
        # Add date if it isn't present
        if not "date" in argumentValues.keys():
            argumentValues["date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")


        playerRuns = [x[1] for x in dbm.getPlayerRuns(runnerID, argumentValues["category"])]

        # Don't accept duplicate times
        if time in playerRuns:
            return "Run already tracked"
        
        # Don't accept worse times
        if len(playerRuns) > 0:
            if time > min(playerRuns):
                return "Faster run for this runner already tracked!"


        dbm.insertRun(argumentValues["category"], time, argumentValues["date"], runnerID)
        dbm.generateLeaderboard("inbounds")

        return f"Run submitted on behalf of {argumentValues['runner']}"