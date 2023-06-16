import sqlite3
import os
import srcomAPIHandler
import durations
import csv
import json
import time as timeModule
import sanitisation
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

# Maps where you have to be using the wr route to be eligible for comgold
comgoldEligibility = {
    "oob": [
        "testchmb_a_00"
    ],
    "inbounds": [
        "testchmb_a_01",
        "testchmb_a_09",
        "testchmb_a_11"
    ],
    "unrestricted": [],
    "legacy": [],
    "glitchless": []
}

def insertTolAccount(name: str, discordID: str = None, srcomID: str = None):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    command = "INSERT INTO tolAccounts (Name"
    secondPhrase = "VALUES (?"
    bindings = [name]

    if discordID:
        command += ", discordID"
        secondPhrase += ", ?"
        bindings.append(discordID)
        

    if srcomID:
        command += ", srcomID"
        secondPhrase += ", ?"
        bindings.append(srcomID)

    command += ") "
    command += secondPhrase
    command += ")"

    
    cur.execute(command, bindings)
    
    conn.commit()


def insertSrcomAccount(id, name):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO srcomAccounts (ID, Name) VALUES (?, ?)", (id, name))

    conn.commit()



def insertRun(category: str, time: float, date: str, tolAccount: int = None, srcomAccount: str = None, srcomID: str = None):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO runs (category, time, date, tolAccount, srcomAccount, srcomID) VALUES (?, ?, ?, ?, ?, ?)", (category, time, date, tolAccount, srcomAccount, srcomID))
    conn.commit()
    
def insertOrUpdateSetupElement(tolID, element, value):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(tolAccountID) FROM setupElements WHERE tolAccountID=? AND element=?", (tolID, element))
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO setupElements VALUES (?, ?, ?)", (tolID, element, value))

    else:
        cur.execute("UPDATE setupElements SET value = ? WHERE tolAccountID=? AND element=?", (value, tolID, element))

    conn.commit()

def insertIL(level: str, category: str, time: float, date: str, tolAccount: int = None, srcomAccount: str = None, srcomID: str = None):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO ilRuns (level, category, time, date, tolAccount, srcomAccount, srcomID) VALUES (?, ?, ?, ?, ?, ?, ?)", (level, category, time, date, tolAccount, srcomAccount, srcomID))
    idNum = cur.lastrowid
    conn.commit()
    return idNum


def userAlreadyRegistered(discordID: str) -> bool:
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT discordID FROM tolAccounts WHERE discordID = ?", (discordID,))
    count = len(cur.fetchall())
    conn.close()
    if count:
        return True
    else:
        return False
    

def getSrcomIDFromDiscordID(discordID: str) -> str:
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT srcomID FROM tolAccounts WHERE discordID = ?", (discordID,))

    result = cur.fetchall()
    conn.close()
    if len(result) == 0:
        return None
    else:
        return result[0][0]
    


def getSrcomIDFromSrcomName(srcomName: str):
    ## Function obsoleted, idk if will make work again
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()

    cur.execute("SELECT ID FROM srcomAccounts WHERE name = ?", (srcomName,))
    result = cur.fetchall()
    count = len(result)
    # If we already have a runner in the database with that name, grab the srcom ID from the database
    if count:
        return result[0][0]
    else: # If we don't already have that runner (which is unlikely, but technically not impossible) then get the ID from srcom api
        return srcomAPIHandler.getIDFromName(srcomName)
        # We won't write it to the database here, as that will be done in the registration function


def srcomIDAlreadyInUse(srcomID: str) -> bool:
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT ID FROM tolAccounts WHERE srcomID = ? AND discordID NOT NULL", (srcomID,))
    count = len(cur.fetchall())
    conn.close()
    if count:
        return True
    else:
        return False
    

def updateSrcomID(discordID: str, newSrcomID: str):
    # This is shorthand for finding the player ID using the discord ID and then updating the srcomID for the entry with that playerID; discordID is not a primary key
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("UPDATE tolAccounts SET srcomID = ? WHERE discordID = ?", (newSrcomID, discordID))
    conn.commit()



def getTolAccountID(discordID: str = None, srcomID: str = None):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    
    if discordID:
        cur.execute("SELECT ID FROM tolAccounts WHERE discordID = ?", (discordID,))

    elif srcomID:
        cur.execute("SELECT ID FROM tolAccounts WHERE srcomID = ?", (srcomID,))

    else:
        return False
    
    result = cur.fetchone()
    if result:
        playerID = result[0]
    else:
        playerID = False
    conn.close()
    return playerID


def getSrcomIDFromTolID(tolAccount):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT srcomID FROM tolAccounts WHERE ID = ?", (tolAccount,))

    result = cur.fetchall()
    conn.close()
    if len(result) == 0:
        return None
    else:
        return result[0][0]


def getPlayerRuns(tolAccount="", category="", includeSrcom=True, propagate=True, srcomID=None):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    if includeSrcom:
        if not srcomID:
            srcomID = getSrcomIDFromTolID(tolAccount)
    else:
        srcomID = ""    
    if propagate:
        cur.execute("""
        SELECT hierarchy
        FROM categoryHierarchy
        WHERE categoryName = ?
        """, (category,))
        categoryHierarchy = cur.fetchone()[0]
        cur.execute(
            """
                SELECT ID, time 
                FROM runs
                LEFT JOIN categoryHierarchy ON runs.category = categoryHierarchy.categoryName
                WHERE categoryHierarchy.hierarchy >= ? AND (tolAccount = ? OR srcomAccount = ?)
        """, (categoryHierarchy, tolAccount, srcomID))

    else:
        cur.execute(
            """
            SELECT ID, time 
            FROM runs
            WHERE category = ? AND (tolAccount = ? OR srcomAccount = ?)
        """, (category, tolAccount, srcomID))
    runs = cur.fetchall()
    conn.close()
    return runs


def getPb(tolAccount, category, includeSrcom=True, srcomID=None):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    if not srcomID:
        cur.execute(
        """
        SELECT ID, MIN(time) 
        FROM runs
        LEFT JOIN categoryHierarchy ON runs.category = categoryHierarchy.categoryName
        WHERE categoryHierarchy.hierarchy >= (
        SELECT hierarchy
        FROM categoryHierarchy
        WHERE categoryName = ?
        )
        AND (tolAccount = ? OR srcomAccount = (
        SELECT srcomID FROM tolAccounts WHERE ID = ?
        ))
    """, (category, tolAccount, tolAccount))
    else:
        cur.execute(
        """
        SELECT ID, MIN(time) 
        FROM runs
        LEFT JOIN categoryHierarchy ON runs.category = categoryHierarchy.categoryName
        WHERE categoryHierarchy.hierarchy >= (
        SELECT hierarchy
        FROM categoryHierarchy
        WHERE categoryName = ?
        )
        AND srcomAccount = ?""", (category, srcomID))
  

    run = cur.fetchone()
    conn.close()
    return run


def getTolIDFromILID(ILID: int):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT tolAccount FROM ilRuns WHERE ID = ?", (ILID,))
    result = cur.fetchall()
    conn.commit()
    if len(result) >= 1:
        return result[0][0]
    else:
        return False
    
def getNameFromTolID(tolID: int, clip: int = 12):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM tolAccounts WHERE ID = ?", (tolID,))
    result = cur.fetchall()
    conn.commit()
    if len(result) >= 1:
        return sanitisation.sanitiseString(result[0][0][:clip-1])
    else:
        return False


    
def addDiscordToPlayer(discordID, srcomID):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("UPDATE players SET discordID = ? WHERE srcomID = ?", (discordID, srcomID))
    conn.commit()



def srcomAccountTracked(srcomAccountId: str) -> bool:
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT ID FROM srcomAccounts WHERE ID = ?", (srcomAccountId,))
    results = len(cur.fetchall())
    conn.close()
    if results == 1:
        return True
    else:
        return False
    

def runTracked(srcomID):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT ID FROM runs WHERE srcomid = ?", (srcomID,))
    results = cur.fetchall()
    conn.close()
    if len(results) > 0:
        return results[0][0]
    else:
        return False
    

def identicalRunTracked(srcomAccount, category, time):
    tolAccount = getTolAccountID(srcomID=srcomAccount)
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT ID FROM runs WHERE (srcomAccount = ? OR tolAccount = ?) AND category = ? AND time = ?", (srcomAccount, tolAccount, category, time))
    results = len(cur.fetchall())
    conn.close()
    if results > 0:
        return True
    else:
        return False
    

def generateLeaderboard(category):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT hierarchy
    FROM categoryHierarchy
    WHERE categoryName = ?
    """, (category,))
    categoryHierarchy = cur.fetchone()[0]
    cur.execute(
        """
        SELECT COALESCE(ta.Name, sa.Name), r.ID, MIN(r.time)
        FROM runs r
        LEFT JOIN tolAccounts ta on r.tolAccount = ta.ID OR r.srcomAccount = ta.srcomID
        LEFT JOIN srcomAccounts sa on r.srcomAccount = sa.ID
        LEFT JOIN categoryHierarchy ch on r.category = ch.categoryName
        WHERE ch.hierarchy >= ?
        GROUP BY COALESCE(ta.ID, 'N/A'), COALESCE(ta.srcomID, sa.ID, 'N/A')
        ORDER BY r.time ASC
        """, (categoryHierarchy,))
    
    result = cur.fetchall()
    output = {}
    for run in result:
        time = run[2]
        name = sanitisation.sanitiseString(run[0])
        if name in output.keys():
            if time < output[name]["t"]:
                output[name] = {"t": time, "id": run[1]}
        else:
            output[name] = {"t": time, "id": run[1]}

    with open(dirPath+"/leaderboardReferences/"+category+".json", "w", newline="") as f:
        placementDict = {}
        currentTime = -1
        placement = 0
        truePlacement = 0
        for runner in output.keys():
            truePlacement += 1
            if output[runner]["t"] > currentTime:
                placement = truePlacement
            currentTime = output[runner]["t"]   
            placementDict[output[runner]["id"]] = placement

        json.dump(placementDict, f)

    
    actualOutput = []
    for runner in output.keys():
        actualOutput.append([runner, durations.formatted(output[runner]["t"]), placementDict[output[runner]["id"]]])
    
    return actualOutput





def fetchLeaderboardPlace(runID, category=None):
    if not category:
        category = getCategoryFromRunID(runID)
    if not category:
        return False
    with open(dirPath+"/leaderboardReferences/"+category+".json", "r") as f:
        reference = json.load(f)

    if str(runID) in reference.keys():
        return reference[str(runID)]
    else:
        return False

    
def fetchILPlace(runID, category=None):
    if not category:
        category = getCategoryFromILID(runID)
    level = getLevelFromILID(runID)
    if not level:
        return False
    if not category:
        return False
    with open(dirPath+"/leaderboardReferences/"+level+"_"+category+".json", "r") as f:
        reference = json.load(f)

    if str(runID) in reference.keys():
        return reference[str(runID)]
    else:
        return False

            

def getTolIDFromName(name: str):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT ID FROM tolAccounts WHERE LOWER(name) = ?", (name.lower(),))
    results = cur.fetchall()
    if len(results) > 0:
        return results[0][0]
    else:
        return False
    

def getCategoryFromRunID(runID):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT category FROM runs WHERE ID = ?", (runID,))
    results = cur.fetchall()
    if len(results) > 0:
        return results[0][0]
    else:
        return False
    
def getCategoryFromILID(ILID):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT category FROM ilRuns WHERE ID = ?", (ILID,))
    results = cur.fetchall()
    conn.close()
    if len(results) > 0:
        return results[0][0]
    else:
        return False
    
def getLevelFromILID(ILID):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT level FROM ilRuns WHERE ID = ?", (ILID,))
    results = cur.fetchall()
    conn.close()
    if len(results) > 0:
        return results[0][0]
    else:
        return False
    
def addSrcomIDToRun(runID, srcomID):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("UPDATE runs SET srcomID = ? WHERE ID = ?", (srcomID, runID))
    conn.commit()


def getSetupFromTolID(tolID):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT element, value FROM setupElements WHERE tolAccountID = ?", (tolID,))
    results = cur.fetchall()
    conn.close()
    if len(results) > 0:
        return results
    else:
        return False

def generateILBoard(level, category):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT hierarchy
    FROM categoryHierarchy
    WHERE categoryName = ?
    """, (category,))
    categoryHierarchy = cur.fetchone()[0]
    cur.execute(
        """
        SELECT tolAccounts.name, MIN(ilRuns.time), ilRuns.ID
        FROM ilRuns
        LEFT JOIN tolAccounts ON ilRuns.tolAccount = tolAccounts.ID
        LEFT JOIN categoryHierarchy ON ilRuns.category = categoryHierarchy.categoryName
        WHERE categoryHierarchy.hierarchy >= ?
        AND level = ?
        GROUP BY tolAccounts.ID

        ORDER BY ilRuns.time
        """, (categoryHierarchy, level))
    
    result = cur.fetchall()
    print(result)
    conn.close()
    output = {}
    for run in result:
        time = run[1]
        name = run[0]
        if name in output.keys():
            if time < output[name]["t"]:
                output[name] = {"t": time, "id": run[2]}
        else:
            output[name] = {"t": time, "id": run[2]}

    """
    with open(dirPath+"/leaderboardReferences/"+level+"_"+category+".csv", "w", newline="") as f:
        c = csv.writer(f)
        for runner in output.keys():
            c.writerow([output[runner]["id"]])
    """

    with open(dirPath+"/leaderboardReferences/"+level+"_"+category+".json", "w", newline="") as f:
        placementDict = {}
        currentTime = -1
        placement = 0
        truePlacement = 0
        for runner in output.keys():
            truePlacement += 1
            if output[runner]["t"] > currentTime:
                placement = truePlacement
            currentTime = output[runner]["t"]   
            placementDict[output[runner]["id"]] = placement

        json.dump(placementDict, f)

        

    
    actualOutput = []
    for runner in output.keys():
        actualOutput.append([output[runner]["id"], runner, durations.formatted(output[runner]["t"])])
    
    return actualOutput


def getRunnerILPBs(tolAccount):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT ID, level, category, MIN(time)
    FROM ilRuns
    WHERE tolAccount = ?
    GROUP BY level, category
    """, (tolAccount,))
    result = cur.fetchall()
    conn.close()
    return result

def getILWRs():
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT ilRuns.ID, level, category, MIN(time), tolAccounts.Name
    FROM ilRuns
    LEFT JOIN tolAccounts ON ilRuns.tolAccount = tolAccounts.ID
    GROUP BY level, category
    """)
    result = cur.fetchall()
    conn.close()
    return result



def updateILBoardLight(levels = levelNames.keys(),
                  categories = ["oob", "inbounds", "glitchless"]):
    for level in levels:
        for category in categories:
            generateILBoard(level, category)


def updateLeaderboardLight(categories = ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]):
    for category in categories:
        generateLeaderboard(category)


def getSumOfBest(tolAccount: int, category: str) -> dict:
    """
    Returns a dictionary containing a user's golds for every map, keyed to the level name
    """

    golds = {x: "" for x in levelNames.values[:17]}
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT level, time
    FROM ilRuns
    WHERE category = ? AND tolAccount = ?
    """, (category, tolAccount))
    result = cur.fetchall()
    conn.close()

    for gold in result:
        golds[levelNames[result[0]]] = result[1]



def getMapFromLevelName(levelName):
    return list(levelNames.keys())[list(levelNames.values()).index(levelName)]


def updateTolName(tolAccount, newName):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    UPDATE tolAccounts 
    SET Name = ?
    WHERE ID=?
    """, (newName, tolAccount))
    result = cur.fetchall()
    conn.commit()
    conn.close()


def deleteRun(runID):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM runs WHERE ID = ?", (runID,))
    conn.commit()


def getDiscordIDFromName(name: str):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT discordID FROM tolAccounts WHERE LOWER(name) = ?", (name,))
    results = cur.fetchall()
    if len(results) > 0:
        return results[0][0]
    else:
        return False
    
    


def getAverageRank(tolAccount, leaderBoardReferences: dict = None, srcomAccount = None, ):
    if not leaderBoardReferences:
        leaderBoardReferences = {}
        for cat in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
            with open(dirPath+"/leaderBoardReferences/"+cat+".json", "r") as f:
                leaderBoardReferences[cat] = json.load(f)


    totalCategories = 0
    totalPlaces = 0
    weights = {
        "oob": 10,
        "inbounds": 10,
        "unrestricted": 1,
        "legacy": 10,
        "glitchless": 10
    }

    for cat in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
        if srcomAccount:
            pb = getPb("", cat, srcomID=srcomAccount)
        else:
            pb = getPb(tolAccount, cat)

 
        if not pb[0]:
            return (None, 0)
            
        
        place = leaderBoardReferences[cat][str(pb[0])]*weights[cat]
        totalPlaces += place
        totalCategories += 1


            
        

    return (round(totalPlaces/sum(weights.values()), 2), totalCategories)

    

def getRunnerAccounts():
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT tolAccounts.ID, srcomAccounts.ID, COALESCE(tolAccounts.Name, srcomAccounts.Name)
    FROM tolAccounts
    FULL OUTER JOIN srcomAccounts
    ON tolAccounts.srcomID = srcomAccounts.ID
    """)
    results = cur.fetchall()
    conn.close()
    if len(results) > 0:
        return results
    else:
        return False
    

def getAverageRankLeaderboard(useCache=True):
    if useCache:
        with open(dirPath+"/leaderboardReferences/averageRankLeaderboard.json", "r") as f:
            averageRanks = json.load(f)
        return averageRanks


    # Load the placement references into memory for quick access
    placementReferences = {}
    for cat in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
        with open(dirPath+"/leaderBoardReferences/"+cat+".json", "r") as f:
            placementReferences[cat] = json.load(f)



    accounts = getRunnerAccounts()
    averageRanks = []
    for account in accounts:
        # account[0] is tol id, account[1] is srcom id
        if account[1] and not account[0]:
            averageRank = getAverageRank("", placementReferences, account[1])
        else:
            averageRank = getAverageRank(account[0], placementReferences)

        if averageRank[1] == 5:
            averageRanks.append((account[2], averageRank[0]))

    



    averageRanks = sorted(averageRanks, key=lambda x: x[1])
    with open(dirPath+"/leaderboardReferences/averageRankLeaderboard.json", "w") as f:
        json.dump(averageRanks, f)
    return averageRanks



def updateSrcomRunTime(runID, time):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    UPDATE runs 
    SET time = ?
    WHERE srcomID = ?
    """, (time, runID))
    result = cur.fetchall()
    conn.commit()
    conn.close()


def addOrUpdateGold(tolID, category, map, time):
    
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(userID) FROM golds WHERE userID=? AND category=? AND map=?", (tolID, category, map))
    if cur.fetchone()[0] == 0:
        if map in comgoldEligibility[category]:
            eligible = "no"
        else:
            eligible = "yes"
        cur.execute("INSERT INTO golds VALUES (?, ?, ?, ?, ?)", (tolID, category, map, time, eligible))

    else:
        cur.execute("UPDATE golds SET time = ? WHERE userID=? AND category=? AND map=?", (time, tolID, category, map))

    conn.commit()


def grabGolds(tolID, category):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT map, time
    FROM golds
    WHERE userID = ? AND category = ?
    """, (tolID, category))
    result = cur.fetchall()
    conn.close()
    return result


def getCommgolds(category):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT ta.Name, golds.map, MIN(golds.time)
    FROM golds
    LEFT JOIN tolAccounts ta on ta.ID = golds.userID
    WHERE CATEGORY = ? AND comgoldEligible = "yes"
    GROUP BY golds.map
    """, (category,))
    result = cur.fetchall()
    conn.close()
    return result


def getComgoldEligibility(tolID, category, map):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT comgoldEligible
    FROM golds
    WHERE userID = ? AND category = ? AND map = ?
    """, (tolID, category, map))
    result = cur.fetchone()
    conn.close()
    return result


def updateComgoldEligibility(eligible, tolID, category, map):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    UPDATE golds
    SET comgoldEligible = ?
    WHERE userID=? AND category=? AND map=?
    """, (eligible, tolID, category, map))
    conn.commit()



def generateAMCBoard():
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT COALESCE(runs.tolAccount, ta.ID), COALESCE(runs.srcomAccount, ta.srcomID), COALESCE(ta.Name, src.Name), category, MIN(runs.time) AS fastestTime
    FROM runs
    LEFT JOIN tolAccounts ta on (runs.srcomAccount = ta.srcomID) OR (runs.tolAccount = ta.ID)
    LEFT JOIN srcomAccounts src on (runs.srcomAccount = src.ID) OR (ta.srcomID = src.ID)

    GROUP BY COALESCE(COALESCE(runs.tolAccount, ta.ID), COALESCE(runs.srcomAccount, ta.srcomID)), category
        
    """)
    results = cur.fetchall()
    conn.close()

    sums = {}

    for result in results:
        identifier = str(result[0]) + "-" + result[1]
        if not identifier in sums.keys():
            sums[identifier] = {"name": result[2], "time": 0, "contributed": 0}

        if result[3] in ["oob", "inbounds", "legacy", "glitchless"]:
            sums[identifier]["time"] += result[4]
            sums[identifier]["contributed"] += 1

    board = []
    for value in sums.values():
        if value["contributed"] == 4:
            board.append({"name": value["name"], "time": value["time"]})
        
    board = sorted(board, key = lambda x: x["time"])
    return board
