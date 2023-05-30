import cobble.command
import cobble.validations
import discord
import databaseManager as dbm

class RefreshLeaderboardsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Refresh Leaderboards", "refresh", "Refresh the leaderboard caches for all categories", cobble.permissions.ADMIN)

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        dbm.updateLeaderboardLight()
        return "Leaderboards updated"