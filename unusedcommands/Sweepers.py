import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

class SweepersCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Top X Sweepers", "sweepers", "Check who has a time in the top X in all categories", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("cutoff", "The x in top X", cobble.validations.IsInteger()))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        cutoff = int(argumentValues["cutoff"])
        sweepers = []
        runners = dbm.getRunnerAccounts()
        for runner in runners:
            validCats = 0
            for cat in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
                if runner[0]:
                    pb = dbm.getPb(runner[0], cat)
                else:
                    pb = dbm.getPb("", cat, srcomID=runner[1])
                if pb[0]:
                    placement = dbm.fetchLeaderboardPlace(pb[0], cat)
                    if placement <= cutoff:
                        validCats += 1
                    else:
                        break

            if runner[2] == "Shizzal":
                print(validCats)
            if validCats == 5:
                sweepers.append(runner[2])

        output = f"People with Top {cutoff} in all Categories:"
        for sweeper in sweepers:
            output += "\n"+sweeper
        
        return output