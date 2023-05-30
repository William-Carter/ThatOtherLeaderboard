import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import durations
import datetime



class SubmitCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Submit", "submit", "Submit a run to the leaderboard", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category your run is of", IsCategory()))
        self.addArgument(cobble.command.Argument("time", "The duration of your run", IsDuration()))
        self.addArgument(cobble.command.Argument("date", "The date your run was performed on", cobble.validations.IsISO8601(), True))


    def postCommand(self):
        dbm.updateLeaderboardLight()
        dbm.getAverageRankLeaderboard(False)

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        time =  durations.correctToTick(durations.seconds(argumentValues["time"])) # Convert entered time to seconds and correct to the nearest tick value
        runnerID = dbm.getTolAccountID(discordID = messageObject.author.id)
        if not runnerID:
            return "User is not registered. Please register with .register to submit runs."
        
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
                return "Faster run already tracked!"


        dbm.insertRun(argumentValues["category"], time, argumentValues["date"], runnerID)
        

        return "Run submitted"