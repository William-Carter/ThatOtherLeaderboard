import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import srcomAPIHandler

class RegisterCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """

        super().__init__(bot, "Register", "register", "Register an account with That Other Leaderboard", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("srcomName", "The username of your speedrun.com account", cobble.validations.IsString()))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict):
        """
        Generate a profile for the given player (or the sender, if no player is provided)
        Parameters:
            messageObject - the object corresponding to the message that triggered the command
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        Returns:
            output - A table displaying the leaderboard
        """
        srcomID = srcomAPIHandler.getIDFromName(argumentValues['srcomName'])
        if not srcomID: 
            return f"No speedrun.com account with name {argumentValues['srcomName']}!"
    
        if dbm.srcomIDAlreadyInUse(srcomID):
            if srcomID == dbm.getSrcomIDFromDiscordID(messageObject.author.id):
                return "You're already registered with that username."
            
            else:
                return "Speedrun.com account already linked to another user. Contact an administrator if you believe this to be a mistake."
            
        
        if dbm.userAlreadyRegistered(messageObject.author.id):
            if dbm.srcomAccountTracked(srcomID):
                dbm.updateSrcomID(messageObject.author.id, srcomID)
                
            else:
                dbm.insertSrcomAccount(srcomID, argumentValues['srcomName'])
                dbm.updateSrcomID(messageObject.author.id, srcomID)
        
            return "Speedrun.com account updated to "+argumentValues['srcomName']
        else:
            if dbm.srcomAccountTracked(srcomID):
                dbm.insertTolAccount(messageObject.author.name, messageObject.author.id, srcomID)
                return f"{messageObject.author.name} is now linked to an existing entry for {argumentValues['srcomName']}"
            
            else:
                dbm.insertSrcomAccount(srcomID, argumentValues['srcomName'])
                dbm.insertTolAccount(argumentValues['srcomName'], messageObject.author.id, srcomID)
                return f"{messageObject.author.name} is now linked to a new entry for {argumentValues['srcomName']}"
