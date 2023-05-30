import cobble.command
import cobble.validations
import discord
import databaseManager as dbm
from customcommands.customvalidations import *

import untitledParserParser as upp
import neatTables

import time as timeModule
import os
import zipfile
import shutil

dirPath = os.path.dirname(os.path.realpath(__file__))

class BatchSubmitCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Batch submit IL", "batch", "Submit a batch of ILs to the leaderboard", cobble.permissions.TRUSTED)
        self.addFileArgument(cobble.command.FileArgument("Demo Archive", "A zip file containing all the demos you want to submit. Demos must have the category in the filename", "zip"))

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        await messageObject.channel.send("Processing demos, this may take a moment")
        tolAccount = dbm.getTolAccountID(discordID=messageObject.author.id)
        attachment = attachedFiles["Demo Archive"]
        demoPath = dirPath+"/demos/temp/"+str(attachment.id)
        with open(demoPath+".zip", "wb") as f:
            demoBytes = await attachment.read()
            f.write(demoBytes)
        
        with zipfile.ZipFile(demoPath+".zip", 'r') as zip_ref:
            zip_ref.extractall(demoPath+"/")


        workingPath = demoPath+"/"

        extractedFiles = os.listdir(workingPath)
        

        # You often end up with a folder containing the zipped files inside the zip, so we'll work in that folder if it exists
        if len(extractedFiles) == 1:
            if extractedFiles[0].split(".")[-1] != "dem":
                workingPath += extractedFiles[0]+"/"
                extractedFiles = os.listdir(workingPath)



        demoStatuses = {}

        for file in extractedFiles:
            demoStatuses[file] = {"map": "", "category": "", "time": "", "status":""}
            if file.split(".")[-1] == "dem":
                
                date = timeModule.gmtime(os.path.getmtime(workingPath+file))
                date_formatted = f"{date[0]}-{date[1]}-{date[2]}"
                demo = upp.DemoParse(workingPath+file)
                if not demo.valid:
                    demoStatuses[file]["status"] = "Invalid demo file"
                    continue
                category = self.determineDemoCategory(file)
                
                if not category:
                    demoStatuses[file]["status"] = "No category detected"
                    continue

                demoStatuses[file]["category"] = category
                level = demo.map
                demoStatuses[file]["map"] = dbm.levelNames[demo.map]
                adjustedtime = demo.time
                if demo.map == "testchmb_a_00" and not demo.specialTimingPoint:
                    adjustedtime += 53.025

                demoStatuses[file]["time"] = durations.formatted(adjustedtime)
                ilID = dbm.insertIL(level, category, adjustedtime, date_formatted, tolAccount)
                folderPath = dirPath+"/demos/ILs/"+str(ilID)
                os.mkdir(folderPath)
                os.rename(workingPath+file, folderPath+"/"+str(ilID)+".dem")

                demoStatuses[file]["status"] = "Success!"
    
            else:
                demoStatuses[file]["status"] = "File not demo!"

            
        shutil.rmtree(demoPath)
        
        output = "Results:\n"
        tableData = [["File", "Level", "Category", "Time", "Status"]]
        for file in demoStatuses.keys():
            tableData.append([file, demoStatuses[file]["map"], demoStatuses[file]["category"], demoStatuses[file]["time"], demoStatuses[file]["status"]])

        table = "```"+neatTables.generateTable(tableData)+"```"
        output += table
        dbm.updateILBoardLight()
        return output
    

    def determineDemoCategory(self, filename:str) -> str:
        patterns = {
            "oob":          r"(?<![bn])o",
            "inbounds":     r"(?<!l)i(?!l)|no?sla",
            "glitchless":   r"g"
        }

        for category in patterns.keys():
            if bool(re.search(patterns[category], filename)):
                return category
            
        return None