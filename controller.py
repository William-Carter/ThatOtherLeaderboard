import dbManager
import datetime
import durations
import srcomAPIHandler
import sheetsInterface
import os
import zipfile
import untitledParserParser
import time
import regex as re
import shutil
import neatTables
import asyncio
dirPath = os.path.dirname(os.path.realpath(__file__))


levelNames = {
        "testchmb_a_00": "00/01",
        "testchmb_a_01": "02/03",
        "testchmb_a_02": "04/05",
        "testchmb_a_03": "06/07",
        "testchmb_a_04": "08",
        "testchmb_a_05": "09",
        "testchmb_a_06": "10",
        "testchmb_a_07": "11/12",
        "testchmb_a_08": "13",
        "testchmb_a_09": "14",
        "testchmb_a_10": "15",
        "testchmb_a_11": "16",
        "testchmb_a_13": "17",
        "testchmb_a_14": "18",
        "testchmb_a_15": "19",
        "escape_00": "e00",
        "escape_01": "e01",
        "escape_02": "e02",
        "testchmb_a_08_advanced": "a13",
        "testchmb_a_09_advanced": "a14",
        "testchmb_a_10_advanced": "a15",
        "testchmb_a_11_advanced": "a16",
        "testchmb_a_13_advanced": "a17",
        "testchmb_a_14_advanced": "a18"
    }

categories = ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]


def correctToTick(time: float) -> float:
    timeDiv = round(round((time/0.015), 0)*0.015, 3)
    return timeDiv


def registerPlayer(discordName: str, discordID: str, srcomName: str) -> str:
    srcomID = srcomAPIHandler.getIDFromName(srcomName)
    
    if srcomID == False:
        return "Failed to register; Speedrun.com account not found"
    

    if dbManager.srcomIDAlreadyInUse(srcomID):
            if srcomID == dbManager.getSrcomIDFromDiscordID(discordID):
                return "You're already registered with that username."
            
            else:
                return "Speedrun.com account already linked to another user. Contact a moderator if you believe this to be a mistake."

    if dbManager.userAlreadyRegistered(discordID):
            if dbManager.srcomAccountTracked(srcomID):
                dbManager.updateSrcomID(discordID, srcomID)
                
            else:
                dbManager.insertSrcomAccount(srcomID, srcomName)
                dbManager.updateSrcomID(discordID, srcomID)
        
            return "Speedrun.com account updated to "+srcomName
    else:
        if dbManager.srcomAccountTracked(srcomID):
            dbManager.insertTolAccount(discordName, discordID, srcomID)
            return f"{discordName} is now linked to an existing entry for {srcomName}"
        
        else:
            dbManager.insertSrcomAccount(srcomID, srcomName)
            dbManager.insertTolAccount(srcomName, discordID, srcomID)
            return f"{discordName} has been added as a new entry."


def addRun(discordID: str, category: str, time: str, date: str="now", srcomID: str = None, forcePB: bool = False) -> str:
    dateFormat = "%Y-%m-%d"
    playerID = dbManager.getTolAccountID(discordID=discordID)
    if not playerID:
        return "User is not registered. Please register with .register to submit runs."
    # Set date to current utc date if player specified 'now'
    if date == "now":
        date = datetime.datetime.utcnow().strftime(dateFormat)

    try:
        datetime.datetime.strptime(date, dateFormat)
    except:
        return "Invalid date format!"

    timeNum = correctToTick(durations.seconds(time))


    # Check if runner already has a run with this time
    playerRuns = [x[1] for x in dbManager.getPlayerRuns(playerID, category)]
    if timeNum in playerRuns:
        return "Run already tracked"
    
    # Check if player already has a faster run
    if not forcePB:
        if len(playerRuns) > 0:
            if timeNum > min(playerRuns):
                return "Faster run already tracked! To set this run as your PB anyway, submit with -forcepb"
        
    dbManager.insertRun(category, timeNum, date, playerID)  
    updateLeaderboard([category])
    return "Run submitted."


def getProfileFromDiscord(discordID: str):
    tolID = dbManager.getTolAccountID(discordID)
    if not tolID:
        return False
    return getProfile(tolID)


def getProfileFromDiscordName(discordName: str):
    tolID = dbManager.getTolIDFromName(discordName)
    if not tolID:
        return False
    return getProfile(tolID)


def getProfile(tolID: int):

    pbs = {}
    for category in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
        runs = dbManager.getPlayerRuns(tolID, category)

        if len(runs) > 0:
            sortedRuns = sorted(runs, key=lambda x: x[1])
            pbs[category] = sortedRuns[0]
            

    return pbs


def playerRegistered(discordID):
    tolID = dbManager.getTolAccountID(discordID)
    if tolID:
        return True
    else:
        return False


def updateLeaderboard(categories=["oob", "inbounds", "unrestricted", "legacy", "glitchless"]):
    for category in categories:
        sheetsInterface.writeLeaderboard(category, dbManager.generateLeaderboard(category))

async def updateILBoard(levels = levelNames.keys(),
                  categories = ["oob", "inbounds", "glitchless"]):
    for level in levels:
        for category in categories:
            leaderboard = [[x[1], x[2]] for x in dbManager.generateILBoard(level, category)]
            sheetsInterface.writeIlBoard(levelNames[level], category, leaderboard)
            await asyncio.sleep(1)

def updateILBoardLight(levels = levelNames.keys(),
                  categories = ["oob", "inbounds", "glitchless"]):
    for level in levels:
        for category in categories:
            dbManager.generateILBoard(level, category)
def formatLeaderBoardPosition(position: int):
    suffix = "th"
    cases = {"1": "st",
                "2": "nd",
                "3": "rd",
                }
    if not ("0"+str(position))[-2] == "1":
        case = str(position)[-1]
        if case in cases.keys():
            suffix = cases[case]

    return str(position)+suffix


def getRunPlace(runID, category):
    return dbManager.fetchLeaderboardPlace(runID, category)


def getLeaderboard(category, start=1):
    if not category in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
        return "Invalid category!"
    try:
        start= int(start)-1
    except:
        return "Invalid starting position!"

    leaderboard = dbManager.generateLeaderboard(category)[start:]
    response = f"`Leaderboard for {category}:`\n"
    maxNameLength = max([len(x[0]) for x in leaderboard[:20]])
    for i in range(min(len(leaderboard), 20)):
        place = str(i+start+1)
        name = leaderboard[i][0]
        time = leaderboard[i][1]
        time = time+('0'*(3-len(time.split(".")[1]))) # Add trailing 0s
        response += f"`{' '*(2-len(place))}{place}. {name}{' '*(maxNameLength-len(name)+1)} {time}{' '*(9-len(time))}`\n"
    
    return response


def getRunsDisplay(discordID, page=1):
    tolID = dbManager.getTolAccountID(discordID=discordID)
    playerRuns = []
    for category in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
        playerRuns += [[x[0], category, durations.formatted(x[1])] for x in dbManager.getPlayerRuns(tolID, category, includeSrcom=False, propagate=False)]

    responseHead = f"`Showing {min(20, len(playerRuns))} of {len(playerRuns)} runs`\n"
    for run in playerRuns:
        responseHead += f"`{run[0]}, {run[1]}, {run[2]}`\n"


    return responseHead


async def submitIL(category, attachment, date, senderID):
    dateFormat = "%Y-%m-%d"
    if not category in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
        return "Invalid category!"
    
    if date == "now":
        date = datetime.datetime.utcnow().strftime(dateFormat)

    try:
        datetime.datetime.strptime(date, dateFormat)
    except:
        return "Invalid date format!"

    demoPath = dirPath+"/demos/temp/"+str(attachment.id)+".dem"
    with open(demoPath, "wb") as f:
        demoBytes = await attachment.read()
        f.write(demoBytes)
    demo = untitledParserParser.DemoParse(demoPath)
    tolID = dbManager.getTolAccountID(discordID=senderID)
    level = demo.map
    time = demo.time
    if demo.map == "testchmb_a_00" and not demo.specialTimingPoint:
        time += 53.025

    ilID = dbManager.insertIL(level, category, time, date, tolID)
    folderPath = dirPath+"/demos/ILs/"+str(ilID)
    os.mkdir(folderPath)
    os.rename(demoPath, folderPath+"/"+str(ilID)+".dem")

    updateILBoard(levels=[level], categories=[category])
    
    return f"Successfully submitted a time of {durations.formatted(time)} to {levelNames[level]} {category}"


async def submitManyIL(attachment, discordID):
    tolAccount = dbManager.getTolAccountID(discordID=discordID)
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
        if file.split(".")[-1] == "dem":
            date = time.gmtime(os.path.getmtime(workingPath+file))
            date_formatted = f"{date[0]}-{date[1]}-{date[2]}"
            demo = untitledParserParser.DemoParse(workingPath+file)
            category = determineDemoCategory(file)  
            if not category:
                demoStatuses[file] = "No category detected"
                continue

            level = demo.map
            adjustedtime = demo.time
            if demo.map == "testchmb_a_00" and not demo.specialTimingPoint:
                adjustedtime += 53.025

            ilID = dbManager.insertIL(level, category, adjustedtime, date_formatted, tolAccount)
            folderPath = dirPath+"/demos/ILs/"+str(ilID)
            os.mkdir(folderPath)
            os.rename(workingPath+file, folderPath+"/"+str(ilID)+".dem")
            demoStatuses[file] = f"Submitted {levelNames[demo.map]} {category}, {adjustedtime}"
    
    

    
            
            


        else:
            demoStatuses[file] = "File not demo!"

        
    shutil.rmtree(demoPath)
    
    output = "Results:\n"
    for file in demoStatuses.keys():
        output += f"`{file}: {demoStatuses[file]}`\n"


    return output
    

def getSetup(discordID):
    tolID = dbManager.getTolAccountID(discordID=discordID)
    setup = dbManager.getSetupFromTolID(tolID)
    if not setup:
        return "noentries"
    setupDict = {}
    capitalisations = {"sensitivity": "Sensitivity", "mouse": "Mouse", "keyboard": "Keyboard", "dpi": "DPI", "hz": "Hz"}
    for entry in setup:
        element = capitalisations[entry[0]]
        setupDict[element] = entry[1]

    order = {"sensitivity": 2, "mouse": 4, "keyboard": 5, "dpi": 1, "hz": 3}
    setupDict = dict(sorted(setupDict.items(), key= lambda item: order[item[0].lower()]))

    if "Sensitivity" in setupDict.keys() and "DPI" in setupDict.keys():
        edpi = round(int(setupDict["DPI"])*float(setupDict["Sensitivity"]), 3)
        setupDict["Effective DPI"] = edpi

    if len(setupDict) == 0:
        return "nodata"
    
    
    return setupDict


def updateSetup(discordID: str, element: str, value: str):
    element = element.lower()
    acceptedElements = ["keyboard", "mouse", "sensitivity", "dpi", "hz"]
    if not element.lower() in acceptedElements:
        return "Unknown setup element!"
    
    if element == "dpi":
        try:
            inted = int(value)
            if inted < 0:
                return "DPI must be positive!"
            floated = float(value)
            if float(inted) != floated:
                return "DPI must be a valid integer!"
            
        except:
            return "DPI must be a valid integer!"
        
    if element == "sensitivity":
        try:
            floated = float(value)
            if floated < 0:
                return "Sensitivity must be positive!"
        except:
            return "Sensitivity must be a valid number!"
        

    if element == "hz":
        try:
            floated = float(value)
            if floated < 0:
                return "Refresh rate must be positive!"
        except:
            return "Refresh rate must be a valid number!"

    tolID = dbManager.getTolAccountID(discordID=discordID)
    dbManager.insertOrUpdateSetupElement(tolID, element, value)
    return "Setup successfully updated."


def determineDemoCategory(filename:str) -> str:
    patterns = {
        "oob":          r"(?<![bn])o",
        "inbounds":     r"(?<!l)i|no?sla",
        "glitchless":   r"g"
    }

    for category in patterns.keys():
        if bool(re.search(patterns[category], filename)):
            return category
        
    return None


def pullDemo(id):
    demoPath = dirPath+f"/demos/ILs/{id}/{id}.dem"
    demoParse = untitledParserParser.DemoParse(demoPath)
    tolID = dbManager.getTolIDFromILID(id)
    if not tolID:
        return False
    player = dbManager.getNameFromTolID(tolID)
    category = dbManager.getCategoryFromILID(id)
    return {"path": demoPath, "name": player, "category": category, "time": durations.formatted(demoParse.time), "level": levelNames[demoParse.map]}


def getILBoard(level, category, start=1):
    if not level in levelNames.keys():
        if not level in levelNames.values():
            return "Invalid level!"

        else:
            level = list(levelNames.keys())[list(levelNames.values()).index(level)]

        

    
    if not category in ["oob", "inbounds", "glitchless"]:
        return "Invalid category!"
    
    
    try:
        start= int(start)-1
    except:
        return "Invalid starting position!"

    leaderboard = dbManager.generateILBoard(level, category)[start:]
    if len(leaderboard) < 1:
        return "No runs found!"
    response = f"`Leaderboard for {levelNames[level]} {category}:`\n"
    maxNameLength = max([len(x[1]) for x in leaderboard[:20]])
    for i in range(min(len(leaderboard), 20)):
        place = str(dbManager.fetchILPlace(leaderboard[i][0]))
        name = leaderboard[i][1]
        time = leaderboard[i][2]
        time = time+('0'*(3-len(time.split(".")[1]))) # Add trailing 0s
        response += f"`{' '*(2-len(place))}{place}. {name}{' '*(maxNameLength-len(name)+1)} {time}{' '*(9-len(time))}`\n"
    
    return response




def getILPBs(discordID):
    forCats = ["glitchless", "inbounds", "oob"]
    tolAccount = dbManager.getTolAccountID(discordID=discordID)
    pbs = dbManager.getRunnerILPBs(tolAccount)
    tableData = [["Level", "Glitchless", "Inbounds", "Out of Bounds"]]
    for level in levelNames.keys():
        row = [levelNames[level]]
        for category in  forCats:
            relevantPB = ""
            fastestValidRun = []
            for pb in pbs:
                if pb[1] == level and forCats.index(pb[2]) <= forCats.index(category):
                    if pb[3] < fastestValidRun[3]:
                     fastestValidRun = pb
            if len(fastestValidRun) != 0:
                place = dbManager.fetchILPlace(fastestValidRun[0])
                pbTime = fastestValidRun[3]
                relevantPB = f"{durations.formatted(pbTime)}, {formatLeaderBoardPosition(place)}"
                        

            row.append(relevantPB)

        tableData.append(row)

    table = neatTables.generateTable(tableData)
    table = "```\n"+table+"```"
    return table
                


def getRunnerSOILs(tolID: int) -> dict:
    """
    Gets a given runner's Sums of ILs (2 for each category, 1 with advanced maps and 1 without)
    
    Arguments:
        tolID - That other leaderboard account ID

    Returns:
        soils - A dictionary containing all the sums of ils
            Uses standard category names for soils without advanced, uses 'catnameAdv' for soils including them.    
    """
    soils = {"glitchless": 0,
             "glitchlessAdv": 0,
             "inbounds": 0,
             "inboundsAdv": 0,
             "oob": 0,
             "oobAdv": 0}
    
    pbs = dbManager.getRunnerILPBs(tolID)
    

    for pb in pbs:
        soils[pb[2]+"Adv"] += pb[3]
        if not "advanced" in pb[1]:
            soils[pb[2]] += pb[3]


    return soils


def getSoilsDisplay(discordID):
    tableRows = {"glitchless": "Glitchless Std.",
             "glitchlessAdv": "Glitchless Full",
             "inbounds": "Inbounds Std.",
             "inboundsAdv": "Inbounds Full",
             "oob": "Out of Bounds Std.",
             "oobAdv": "Out of Bounds Full"}
    tolAccount = dbManager.getTolAccountID(discordID=discordID)
    soils = getRunnerSOILs(tolAccount)
    tableData = [["Category", "Sum"]]
    for soil in soils.keys():
        tableData.append([tableRows[soil], durations.formatted(soils[soil])])

    table = neatTables.generateTable(tableData)
    table = "```\n"+table+"```"
    return table

def collectILDemo(discordID, level, category):
    if not (level in levelNames.keys() or level in levelNames.values()  ):
        return "?Level invalid"
    if not category in ["glitchless", "inbounds", "oob"]:
        return "?Category invalid"
    tolAccount = dbManager.getTolAccountID(discordID=discordID)
    pbs = dbManager.getRunnerILPBs(tolAccount)
    pbID = -1
    for pb in pbs:
        if (pb[1] == level or pb[1] == getMapFromLevelName(level)) and pb[2] == category:
            pbID = pb[0]

    if pbID >= 0:
        return pullDemo(pbID)
        
    else:
        return "?User has no PB for this category!"

def getMapFromLevelName(levelName: str):
    if not levelName in levelNames.values():
        return False

    else:
        return list(levelNames.keys())[list(levelNames.values()).index(levelName)]

