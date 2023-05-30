import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import neatTables

class SetupCommand(cobble.command.Command):
    capitalisations = {"sensitivity": "Sensitivity", "mouse": "Mouse", "keyboard": "Keyboard", "dpi": "DPI", "hz": "Hz"}
    order = {"sensitivity": 2, "mouse": 4, "keyboard": 5, "dpi": 1, "hz": 3}
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """

        super().__init__(bot, "Setup", "setup", "See a player's setup", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("name", "The name of the user whose profile you want to see", cobble.validations.IsString(), True))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Show the recorded setup for a given player
        Parameters:
            messageObject - the object corresponding to the message that triggered the command
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        Returns:
            response - A string response containing a list of the player's setup elements
        """



        if len(argumentValues.keys()) == 0:
            if not dbm.userAlreadyRegistered(messageObject.author.id):
                return "User must be registered!"
            runnerID = dbm.getTolAccountID(discordID=messageObject.author.id)
            runnerName = messageObject.author.name

        else:
            runnerID = dbm.getTolIDFromName(argumentValues['name'])
            if not runnerID:
                return f"No account associated with {argumentValues['name']}!"
            runnerName = argumentValues['name']


        
        setup = dbm.getSetupFromTolID(runnerID)
        if setup == False:
            return "User has no setup information recorded!\nAdd some with the `updatesetup` command!"



        setupDict = {}
        
        for entry in setup:
            element = self.capitalisations[entry[0]]
            setupDict[element] = entry[1]

        
        setupDict = dict(sorted(setupDict.items(), key= lambda item: self.order[item[0].lower()]))

        if "Sensitivity" in setupDict.keys() and "DPI" in setupDict.keys():
            edpi = round(int(setupDict["DPI"])*float(setupDict["Sensitivity"]), 3)
            setupDict["Effective DPI"] = edpi



        response = f"{runnerName}'s setup:\n```"

        tableData = []
        for type in setupDict.keys():
            tableData.append([type, str(setupDict[type])])

        response += neatTables.generateTable(tableData)
        response += "```"
        return response