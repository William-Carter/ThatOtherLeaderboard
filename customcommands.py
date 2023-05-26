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
import json
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
        return (x.lower() in self.categories)

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
    

class IsNormal(cobble.validations.Validation):
    def __init__(self):
        super().__init__()
        self.requirements = "Don't be an idiot :)"

    def validate(self, x: str):
        bannedChars = r"[@]+|https://|http://"
        if re.search(bannedChars, x):
            return False
        if len(x) > 50:
            return False
        return True

class IsGoldsList(cobble.validations.Validation):
    def __init__(self):
        super().__init__()
        self.requirements = "Must be a list of 18 times, separated by newlines"

    def validate(self, x: str):
        golds = x.split("\n")
        if len(golds) != 18:
            return False
        
        for gold in golds:
            if not IsDuration.validate("", gold):
                return False
        

        return True



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
            runnerName = dbm.getNameFromTolID(runnerID)
            mode = "tol"

        elif "tol" in argumentValues.keys():
            runnerID = dbm.getTolIDFromName(argumentValues["tol"])
            runnerName = argumentValues["tol"]
            mode = "tol"

        elif "srcom" in argumentValues.keys():
            runnerID = dbm.getSrcomIDFromSrcomName(argumentValues["srcom"])
            runnerName = argumentValues["srcom"]
            mode = "srcom"

        tableData = [["Category", "Time", "Place"]]

        forCats = {"oob": "OoB", "inbounds": "Inbounds", "unrestricted": "NoSLA Unr.", "legacy": "NoSLA Leg.", "glitchless": "Glitchless"}
        totalPlaces = 0
        for category in forCats.keys():
            if mode == "tol":
                runs = dbm.getPlayerRuns(runnerID, category)
            elif mode == "srcom":
                runs = dbm.getPlayerRuns("", category, srcomID=runnerID)

            if len(runs) > 0:
                sortedRuns = sorted(runs, key=lambda x: x[1])
                tableCat = forCats[category]
                tableTime = durations.formatted(sortedRuns[0][1])
                place = dbm.fetchLeaderboardPlace(sortedRuns[0][0], category)
                tablePlace = durations.formatLeaderBoardPosition(place)
                totalPlaces += place

                tableData.append([tableCat, tableTime, tablePlace])


        if len(tableData) < 2:
            return "No runs found!"
        output = f"Leaderboard for {runnerName}:\n"
        output += "```"+neatTables.generateTable(tableData)
        if mode == "tol":
            averageRank = dbm.getAverageRank(runnerID)[0]

        elif mode == "srcom":
            averageRank = dbm.getAverageRank("", srcomAccount=runnerID)[0]
        output += f"Average Placement: {averageRank}"+"```"
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
    


class UpdateSetupCommand(cobble.command.Command):

    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """

        super().__init__(bot, "Update Setup", "updatesetup", "Update your setup", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("element", "The part of your setup you want to update", IsSetupElement()))
        self.addArgument(cobble.command.Argument("value", "The value to fill for the specified element", IsNormal()))



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
                if not cobble.validations.IsPositive.validate("", value):
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
        if not demo.valid:
            return f"What the fuck, {messageObject.author.name}"
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
            argumentValues["map"] = dbm.getMapFromLevelName(argumentValues["map"])

        lbData = dbm.generateILBoard(argumentValues["map"], argumentValues["category"])[start:start+20]
        tableData = [["Place", "Runner", "Time"]]
        for entry in lbData:
            place = durations.formatLeaderBoardPosition(dbm.fetchILPlace(entry[0], argumentValues["category"]))
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
        self.addArgument(cobble.command.Argument("tol", "The tol username of the user you want the sum of ILs of", cobble.validations.IsString(), True))


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
    



class SetNameCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Set Name", "setname", "Set your name on TOL", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("name", "The value you want to set your name to", IsNormal()))

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        tolAccount = dbm.getTolAccountID(discordID = messageObject.author.id)
        if dbm.getTolIDFromName(argumentValues["name"]):
            return "This name is already in use"
        dbm.updateTolName(tolAccount, argumentValues["name"])
        return "Account name updated"
    


class RunsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Show Runs", "runs", "List all of a player's runs", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("runner", "The runner whose runs you want to see", cobble.validations.IsString()))
        self.addArgument(cobble.command.Argument("category", "The category of runs you want to see", IsCategory()))


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        discordID = dbm.getDiscordIDFromName(argumentValues["runner"])
        if not discordID:
            return f"No runner registered with name '{argumentValues['runner']}'"
        tolID = dbm.getTolAccountID(discordID=discordID)
        runs = dbm.getPlayerRuns(tolID, argumentValues["category"], False, False)
        tableData = [["RunID", "Time"]]
        for run in runs:
            tableData.append([str(run[0]), durations.formatted(run[1])])
        
        output = f"Runs by {argumentValues['runner']}:\n"
        output += "```"+neatTables.generateTable(tableData)+"```"

        return output
    


class DeleteRunCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Delete run", "delete", "Delete the specified run", cobble.permissions.ADMIN)
        self.addArgument(cobble.command.Argument("runID", "The ID of the run you want to delete", cobble.validations.IsInteger()))
        self.postCommand = lambda: dbm.updateLeaderboardLight()


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        dbm.deleteRun(int(argumentValues["runID"]))
        return "Run deleted"


class BehalfCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Submit on Behalf", "behalf", "Submit a run to the leaderboard on behalf of another user", cobble.permissions.ADMIN)
        self.addArgument(cobble.command.Argument("runner", "The runner who performed the run", cobble.validations.IsString()))
        self.addArgument(cobble.command.Argument("category", "The category of the run", IsCategory()))
        self.addArgument(cobble.command.Argument("time", "The duration of the run", IsDuration()))

    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        time =  round(round((durations.seconds(argumentValues["time"])/0.015), 0)*0.015, 3) # Convert entered time to seconds and correct to the nearest tick value
        
        runnerID = dbm.getTolIDFromName(argumentValues["runner"])
        if not runnerID:
            return f"No registered user with name '{argumentValues['runner']}'"
        
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
                return "Faster run for this runner already tracked!"


        dbm.insertRun(argumentValues["category"], time, argumentValues["date"], runnerID)
        dbm.generateLeaderboard("inbounds")

        return f"Run submitted on behalf of {argumentValues['runner']}"
    

class AverageRankLeaderboardCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Average Rank Leaderboard", "arboard", "Show the leaderboard for average ranks", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("start", "What place to start from", cobble.validations.IsInteger(), True))
        self.addArgument(cobble.command.Argument("useCache", "Whether to use the stored values or recalculate them", cobble.validations.IsBool(), True))
        


    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        if not "start" in argumentValues:
            argumentValues["start"] = 1

        argumentValues["start"] = int(argumentValues["start"])

        
        
        
        useCache = True
        if "useCache" in argumentValues:
            if argumentValues["useCache"] == "false":
                useCache = False
                
            

        averageRanks = dbm.getAverageRankLeaderboard(useCache)[argumentValues["start"]-1:argumentValues["start"]+19]
        
        tableData = [["Place", "Runner", "Average Rank"]]
        for index, entry in enumerate(averageRanks):
            tableData.append([str(index+argumentValues["start"]
                                  )+".", entry[0], str(entry[1])])

        table = "```"+neatTables.generateTable(tableData, padding=2)+"```"
        return table


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
    

class GoldsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Show Golds", "golds", "Show your golds for a given category", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category of your golds", IsCategory()))
    
    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        tolID = dbm.getTolAccountID(discordID=messageObject.author.id)
        golds = dbm.grabGolds(tolID, argumentValues["category"])
        golds = sorted(golds, key= lambda x: list(dbm.levelNames.keys()).index(x[0]))

        

        tableData = [["Level", "Time"]]
        for gold in golds:
            tableData.append([dbm.levelNames[gold[0]], str(durations.formatted(gold[1]))])

        table = neatTables.generateTable(tableData)
        sob = durations.formatted(sum([x[1] for x in golds]))
        table += "\nSum of Best: "+sob

        return f"Golds for {argumentValues['category']}:\n```{table}```"
    

class CommGoldsCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Community Golds", "commgolds", "Show the best golds from all the community", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category of your golds", IsCategory()))
    
    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Generate a leaderboard for the given category
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        golds = dbm.getCommgolds(argumentValues["category"])
        golds = sorted(golds, key= lambda x: list(dbm.levelNames.keys()).index(x[1]))

        tableData = [["Level", "Time", "Runner"]]
        for gold in golds:
            tableData.append([dbm.levelNames[gold[1]], str(durations.formatted(gold[2])), gold[0]])

        table = neatTables.generateTable(tableData)
        sob = durations.formatted(sum([x[2] for x in golds]))
        table += "\nCommunity Sum of Best: "+sob

        return f"Commgolds for {argumentValues['category']}:\n```{table}```"
    

class EligibleCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Set Commgold Eligibilty", "eligible", "Toggle whether your gold for a given level should be considered when finding commgolds.", cobble.permissions.TRUSTED)
        self.addArgument(cobble.command.Argument("category", "The category of your gold", IsCategory()))
        self.addArgument(cobble.command.Argument("level", "The level to update", IsMap()))
    
    async def execute(self, messageObject: discord.message, argumentValues: dict, attachedFiles: dict) -> str:
        """
        Parameters:
            argumentValues - a dictionary containing values for every argument provided, keyed to the argument name
        """
        tolID = dbm.getTolAccountID(discordID=messageObject.author.id)

        if argumentValues["level"] in dbm.levelNames.values():
            argumentValues["level"] = dbm.getMapFromLevelName(argumentValues["level"])

        currentEligiblity = dbm.getComgoldEligibility(tolID, argumentValues["category"], argumentValues["level"])
        if not currentEligiblity:
            return "User does not have this gold!"
        currentEligiblity = currentEligiblity[0]
        print(currentEligiblity)

        response = f"Your gold for {dbm.levelNames[argumentValues['level']]} is "
        if currentEligiblity == "yes":
            newEligibility = "no"
            response += "no longer eligible for commgold"
        else:
            newEligibility = "yes"
            response += "now eligible for commgold"

        dbm.updateComgoldEligibility(newEligibility, tolID, argumentValues["category"], argumentValues["level"])

        return response


class FetchDemoCommand(cobble.command.Command):
    def __init__(self, bot: cobble.bot.Bot):
        """
        Parameters:
            bot - The bot object the command will belong to
        """
        super().__init__(bot, "Fetch IL Demo", "fetchdemo", "Retrieve the demo for an IL", cobble.permissions.EVERYONE)
        self.addArgument(cobble.command.Argument("category", "The category of the demo", IsILCategory()))
        self.addArgument(cobble.command.Argument("level", "The category of your golds", IsMap()))
        self.addArgument(cobble.command.Argument("user", "The person whose demo you want", cobble.validations.IsString(), True))




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
                

