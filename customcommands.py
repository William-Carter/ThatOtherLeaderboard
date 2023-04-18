import cobble.command
import cobble.validations
import databaseManager as dbm
import durations
import neatTables
import discord
import datetime
import srcomAPIHandler
import time as timeModule
import os
import zipfile
import shutil
import untitledParserParser as upp
import regex as re
dirPath = os.path.dirname(os.path.realpath(__file__))

###############
# VALIDATIONS #
###############
class IsCategory(cobble.validations.Validation):
    categories = ["oob", "inbounds", "legacy", "unrestricted", "glitchless"]
    def __init__(self):
        """
        Validate that an argument is a valid TOL category
        """
        super().__init__()
        self.requirements = "Must be one of: "
        for category in self.categories:
            self.requirements += f"{category}, "
        self.requirements = self.requirements[:-2] # remove trailing comma and space


    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it matches any of the predefined categories
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string is a valid category
        """
        return (x in self.categories)

class IsILCategory(cobble.validations.Validation):
    categories = ["oob", "inbounds", "glitchless"]
    def __init__(self):
        """
        Validate that an argument is a valid TOL category
        """
        super().__init__()
        self.requirements = "Must be one of: "
        for category in self.categories:
            self.requirements += f"{category}, "
        self.requirements = self.requirements[:-2] # remove trailing comma and space


    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it matches any of the predefined categories
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string is a valid category
        """
        return (x in self.categories)
    


class IsMap(cobble.validations.Validation):
    categories = ["oob", "inbounds", "glitchless"]
    def __init__(self):
        """
        Validate that an argument is a valid TOL category
        """
        super().__init__()
        self.requirements = "Must be a valid map or level name"


    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it matches any of the predefined categories
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string is a valid category
        """
        return (x in dbm.levelNames.keys() or x in dbm.levelNames.values())


class IsDuration(cobble.validations.Validation):
    def __init__(self):
        super().__init__()
        self.requirements = "Must be a valid amount of time i.e. 47.5, 1:30, 1:17:27.33"

    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it can be parsed into a number of seconds
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string was successfully parsed
        """
        try:
            seconds = durations.seconds(x)
        except:
            return False
        else:
            return True


class IsSetupElement(cobble.validations.Validation):
    def __init__(self):
        super().__init__()
        self.requirements = "Must be one of: "
        for element in SetupCommand.capitalisations.keys():
            self.requirements += f"{element}, "
        self.requirements = self.requirements[:-2] # remove trailing comma and space

    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it can be parsed into a number of seconds
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string was successfully parsed
        """
        return (x in SetupCommand.capitalisations.keys())


############
# COMMANDS #
############


class LeaderboardCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Leaderboard", "leaderboard", "Show the leaderboard for a category", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("category", "The category you wish to see the leaderboard for", IsCategory()))
        self.addArgument(cobble.command.Argument("start", "What place to start from", cobble.validations.IsInteger(), True))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        if "start" in argumentValues.keys():
            start = int(argumentValues["start"])-1
        else:
            start = 0
        lbData = dbm.generateLeaderboard(argumentValues["category"])[start:start+20]
        tableData = [["Place", "Runner", "Time"]]
        for entry in lbData:
            tableData.append([str(entry[2])+".", entry[0], entry[1]])

        table = "```"+neatTables.generateTable(tableData, padding=2)+"```"

        return table



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

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        time =  round(round((durations.seconds(argumentValues["time"])/0.015), 0)*0.015, 3) # Convert entered time to seconds and correct to the nearest tick value
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



class ProfileCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """

        super().__init__(bot, "Profile", "profile", "Show your profile, including all your personal bests", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("tol", "The tol username of the user you want the profile of", cobble.validations.IsString(), True))
        self.addArgument(cobble.command.Argument("srcom", "The srcom username of the user you want the profile of", cobble.validations.IsString(), True))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict):
        """
        Generate a profile for the given player (or the sender, if no player is provided)
        Parameters:
            messageObject - the object corresponding to the message that triggered the command
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        Returns:
            oputput - A table displaying the leaderboard
        """
        if len(argumentValues.keys()) > 1:
            return "Can only return a profile for either a speedrun.com account or a TOL account, not both!"
        
        if len(argumentValues.keys()) == 0:
            runnerID = dbm.getTolAccountID(discordID=messageObject.author.id)
            runnerName = messageObject.author.name

        elif "tol" in argumentValues.keys():
            runnerID = dbm.getTolIDFromName(argumentValues["tol"])
            runnerName = argumentValues["tol"]

        elif "srcom" in argumentValues.keys():
            runnerID = dbm.getTolAccountID(srcomID=dbm.getSrcomIDFromSrcomName(argumentValues["srcom"]))
            runnerName = argumentValues["srcom"]

        tableData = [["Category", "Time", "Place"]]

        forCats = {"oob": "OoB", "inbounds": "Inbounds", "unrestricted": "NoSLA Unr.", "legacy": "NoSLA Leg.", "glitchless": "Glitchless"}
        for category in forCats.keys():
            runs = dbm.getPlayerRuns(runnerID, category)

            if len(runs) > 0:
                sortedRuns = sorted(runs, key=lambda x: x[1])
                tableCat = forCats[category]
                tableTime = durations.formatted(sortedRuns[0][1])
                tablePlace = durations.formatLeaderBoardPosition(dbm.fetchLeaderboardPlace(sortedRuns[0][0], category))

                tableData.append([tableCat, tableTime, tablePlace])

        output = f"Leaderboard for {runnerName}:\n"
        output += "```"+neatTables.generateTable(tableData)+"```"
        return output
        
        

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
            runnerID = dbm.getTolAccountID(discordID=messageObject.author.id)
            runnerName = messageObject.author.name

        else:
            runnerID = dbm.getTolIDFromName(argumentValues['name'])
            if not runnerID:
                return f"No account associated with {argumentValues['name']}!"
            runnerName = argumentValues['name']

        setup = dbm.getSetupFromTolID(runnerID)
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
    


class UpdateSetupCommand(cobble.command.Command):

    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """

        super().__init__(bot, "Update Setup", "updatesetup", "Update your setup", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("element", "The part of your setup you want to update.", IsSetupElement()))
        self.addArgument(cobble.command.Argument("value", "The value to fill for the specified element", cobble.validations.IsString()))



    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Show the recorded setup for a given player
        Parameters:
            messageObject - the object corresponding to the message that triggered the command
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        Returns:
            response - A string response containing a list of the player's setup elements
        """
        element = argumentValues["element"]
        value = argumentValues["value"]

        match element:
            case "dpi":
                if not cobble.validations.IsInteger.validate("", value):
                    return "DPI must be a valid integer!"
                if cobble.validations.IsPositive.validate("", value):
                    return "DPI must be positive!"
                
            case "sensitivity":
                if not cobble.validations.IsNumber.validate("", value):
                    return "Sensitivity must be a number!"
                if not cobble.validations.IsPositive.validate("", value):
                    return "Sensitivity must be positive!"
                
            case "hz":
                if not cobble.validations.IsNumber.validate("", value):
                    return "Refresh rate must be a number!"
                if not cobble.validations.IsPositive.validate("", value):
                    return "Refresh rate must be positive!"
                
            case _:
                pass
                
        tolID = dbm.getTolAccountID(discordID=messageObject.author.id)
        dbm.insertOrUpdateSetupElement(tolID, element, value)
        return "Setup successfully updated."
    
class ILSubmitCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Submit IL", "ilsubmit", "Submit an IL to the leaderboard", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category your run is of", IsILCategory()))
        self.addFileArgument(cobble.command.FileArgument("Demo", "The demo of your IL", "dem"))

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        demoPath = await self.downloadDemo(attachedFiles["Demo"])
        demo = upp.DemoParse(demoPath)
        tolID = dbm.getTolAccountID(discordID=messageObject.author.id)
        level = demo.map
        time = demo.time
        if demo.map == "testchmb_a_00" and not demo.specialTimingPoint:
            time += 53.025
        date = datetime.datetime.utcnow().strftime("%Y-%m-%d")

        ilID = dbm.insertIL(level, argumentValues["category"], time, date, tolID)
        folderPath = dirPath+"/demos/ILs/"+str(ilID)
        os.mkdir(folderPath)
        os.rename(demoPath, folderPath+"/"+str(ilID)+".dem")

        dbm.updateILBoardLight()
        
        return f"Successfully submitted a time of {durations.formatted(time)} to {dbm.levelNames[level]} {argumentValues['category']}"

    async def downloadDemo(self, attachment: discord.Attachment) -> str:
        demoPath = dirPath+"/demos/temp/"+str(attachment.id)+".dem"
        with open(demoPath, "wb") as f:
            demoBytes = await attachment.read()
            f.write(demoBytes)

        return demoPath
    



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
    



class ILBoardCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "IL Leaderboard", "ilboard", "Show the leaderboard for a given IL", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("map", "The IL map", IsMap()))
        self.addArgument(cobble.command.Argument("category", "The IL category", IsILCategory()))
        self.addArgument(cobble.command.Argument("start", "Where to start from", cobble.validations.IsInteger(), True))
        


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        if "start" in argumentValues.keys():
            start = int(argumentValues["start"])-1
        else:
            start = 0

        if argumentValues["map"] in dbm.levelNames.values():
            argumentValues["map"] = list(dbm.levelNames.keys())[list(dbm.levelNames.values()).index(argumentValues["map"])]

        lbData = dbm.generateILBoard(argumentValues["map"], argumentValues["category"])[start:start+20]
        tableData = [["Place", "Runner", "Time"]]
        for entry in lbData:
            place = durations.formatLeaderBoardPosition(dbm.fetchILPlace(entry[0]))
            runner = entry[1]
            time = entry[2]
            tableData.append([place, runner, time])

        table = "```"+neatTables.generateTable(tableData, padding=2)+"```"

        return table
    



class ILPBsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "IL PBs", "ilpbs", "Show your IL pbs", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("tol", "The tol username of the user you want the profile of", cobble.validations.IsString(), True))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        if len(argumentValues.keys()) == 0:
            runnerID = dbm.getTolAccountID(discordID=messageObject.author.id)
            runnerName = messageObject.author.name

        elif "tol" in argumentValues.keys():
            runnerID = dbm.getTolIDFromName(argumentValues["tol"])
            runnerName = argumentValues["tol"]




        forCats = ["glitchless", "inbounds", "oob"]
        pbs = dbm.getRunnerILPBs(runnerID)
        tableData = [["Level", "Glitchless", "Inbounds", "Out of Bounds"]]
        for level in dbm.levelNames.keys():
            row = [dbm.levelNames[level]]
            for category in  forCats:
                relevantPB = ""
                fastestValidRun = []
                for pb in pbs:
                    if pb[1] == level and forCats.index(pb[2]) <= forCats.index(category):
                        if len(fastestValidRun) != 0:
                            if pb[3] < fastestValidRun[3]:
                                fastestValidRun = pb
                        else:
                            fastestValidRun = pb
                if len(fastestValidRun) != 0:
                    place = dbm.fetchILPlace(fastestValidRun[0])
                    pbTime = fastestValidRun[3]
                    relevantPB = f"{durations.formatted(pbTime)}, {durations.formatLeaderBoardPosition(place)}"
                            

                row.append(relevantPB)

            tableData.append(row)

        table = neatTables.generateTable(tableData)
        table = "```\n"+table+"```"
        output = f"IL PBs for {runnerName}:\n"+table
        return output
    
class SumOfILsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Sum of ILs", "soils", "Show your sums of ILs", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("tol", "The tol username of the user you want the profile of", cobble.validations.IsString(), True))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        if len(argumentValues.keys()) == 0:
            runnerID = dbm.getTolAccountID(discordID=messageObject.author.id)
            runnerName = messageObject.author.name

        elif "tol" in argumentValues.keys():
            runnerID = dbm.getTolIDFromName(argumentValues["tol"])
            runnerName = argumentValues["tol"]

        tableRows = {"glitchless": "Glitchless Std.",
                "glitchlessAdv": "Glitchless Full",
                "inbounds": "Inbounds Std.",
                "inboundsAdv": "Inbounds Full",
                "oob": "Out of Bounds Std.",
                "oobAdv": "Out of Bounds Full"}
        soils = {"glitchless": 0,
                "glitchlessAdv": 0,
                "inbounds": 0,
                "inboundsAdv": 0,
                "oob": 0,
                "oobAdv": 0}
        
        pbs = dbm.getRunnerILPBs(runnerID)
        

        for pb in pbs:
            soils[pb[2]+"Adv"] += pb[3]
            if not "advanced" in pb[1]:
                soils[pb[2]] += pb[3]

        tableData = [["Category", "Sum"]]
        for soil in soils.keys():
            tableData.append([tableRows[soil], durations.formatted(soils[soil])])

        table = neatTables.generateTable(tableData)
        table = "```\n"+table+"```"
        return table