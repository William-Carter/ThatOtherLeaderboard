import cobble.command
import cobble.validations
import discord
from customcommands.customvalidations import *

class TicksCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Tick Info", "ticks", "Convert a time to ticks", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("time", "The duration you want to convert", IsDuration()))
    
    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """

        timeString = argumentValues["time"]
        timeNum = durations.seconds(timeString)
        roundedTimeNum = durations.correctToTick(timeNum)
        roundedTimeString = durations.formatted(roundedTimeNum)
        rounded = not (timeNum == roundedTimeNum)
        ticks = int(round(roundedTimeNum/0.015, 0))
        return f"Had to round: {rounded}\nTime: {roundedTimeString}\nTicks: {ticks}"