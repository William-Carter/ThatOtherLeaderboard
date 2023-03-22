import dbManager
import datetime
import math
import durations
import srcomAPIHandler
import sheetsInterface


    


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
        time = time+('0'*(3-len(time.split(".")[1])))
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
    return "Setup succesfully updated."