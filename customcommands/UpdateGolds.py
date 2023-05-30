import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

class UpdateGoldsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Update Golds", "updategolds", "Update your golds on TOL", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category of your golds", IsCategory()))
        self.addArgument(cobble.command.Argument("times", "The times for all your golds, separated by newlines", IsGoldsList()))
    
    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        levels = list(dbm.levelNames.keys())[:18]
        tolID = dbm.getTolAccountID(discordID=messageObject.author.id)
        if not tolID:
            return "Only registered users can submit golds!"

        category = argumentValues["category"]
        goldList = argumentValues["times"].split("\n")

        for index, gold in enumerate(goldList):
            time = durations.correctToTick(durations.seconds(gold))
            dbm.addOrUpdateGold(tolID, category, levels[index], time)

        return "Golds updated!"