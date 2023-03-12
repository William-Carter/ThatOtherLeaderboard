import dbManager
import datetime
import time
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


def getRunPlace(runID):
    return dbManager.fetchLeaderboardPlace(runID)


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