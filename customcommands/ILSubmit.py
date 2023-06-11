import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import untitledParserParser as upp

import os
import datetime

dirPath = os.path.dirname(os.path.realpath(__file__))

class ILSubmitCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Submit IL", ["ilsubmit", "isb"], "Submit an IL to the leaderboard", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category your run is of", IsILCategory()))
        self.addFileArgument(cobble.command.FileArgument("Demo", "The demo of your IL", "dem"))

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        demoPath = await self.downloadDemo(attachedFiles["Demo"])
        demo = upp.DemoParse(demoPath)
        if not demo.valid:
            return f"What the fuck, {messageObject.author.name}"
        tolID = dbm.getTolAccountID(discordID=messageObject.author.id)
        level = demo.map
        time = demo.time
        if demo.map == "testchmb_a_00" and not demo.specialTimingPoint:
            time += 53.025
        date = datetime.datetime.utcnow().strftime("%Y-%m-%d")

        ilID = dbm.insertIL(level, argumentValues["category"], time, date, tolID)
        folderPath = dirPath+"/../demos/ILs/"+str(ilID)
        os.mkdir(folderPath)
        os.rename(demoPath, folderPath+"/"+str(ilID)+".dem")

        dbm.updateILBoardLight()
        
        return f"Successfully submitted a time of {durations.formatted(time)} to {dbm.levelNames[level]} {argumentValues['category']}"

    async def downloadDemo(self, attachment: discord.Attachment) -> str:
        demoPath = dirPath+"/../demos/temp/"+str(attachment.id)+".dem"
        with open(demoPath, "wb") as f:
            demoBytes = await attachment.read()
            f.write(demoBytes)

        return demoPath
    