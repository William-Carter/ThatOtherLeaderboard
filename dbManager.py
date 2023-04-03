import sqlite3
import os
import srcomAPIHandler
import durations
import csv
import json
dirPath = os.path.dirname(os.path.realpath(__file__))






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

    cur.execute("SELECT srcomID FROM players WHERE name = ?", (srcomName,))
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


def getPlayerRuns(tolAccount, category, includeSrcom=True, propagate=True):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    if includeSrcom:
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
    runs = [[x[0], x[1]] for x in cur.fetchall()]
    conn.close()
    return runs


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
    
def getNameFromTolID(tolID: int):
    conn = sqlite3.connect(dirPath+"/tol.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM tolAccounts WHERE ID = ?", (tolID,))
    result = cur.fetchall()
    conn.commit()
    if len(result) >= 1:
        return result[0][0]
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
        SELECT srca.name, srcb.name, MIN(runs.time), runs.ID
        FROM runs 
        LEFT JOIN srcomAccounts srca ON runs.srcomAccount = srca.ID
        LEFT JOIN tolAccounts ON runs.tolAccount = tolAccounts.ID
        LEFT JOIN srcomAccounts srcb ON tolAccounts.srcomID = srcb.ID
        LEFT JOIN categoryHierarchy ON runs.category = categoryHierarchy.categoryName
        WHERE categoryHierarchy.hierarchy >= ?
        GROUP BY srca.ID, tolAccounts.ID, srcb.ID

        ORDER BY runs.time
        """, (categoryHierarchy,))
    
    result = cur.fetchall()
    output = {}
    for run in result:
        time = run[2]
        if run[0]:
            name = run[0]
        else:
            name = run[1]

        if name in output.keys():
            if time < output[name]["t"]:
                output[name] = {"t": time, "id": run[3]}
        else:
            output[name] = {"t": time, "id": run[3]}

    with open(dirPath+"/leaderboardReferences/"+category+".csv", "w", newline="") as f:
        c = csv.writer(f)
        for runner in output.keys():
            c.writerow([output[runner]["id"]])

    with open(dirPath+"/fuck.json", "w") as f:
        json.dump(output, f)

    
    actualOutput = []
    for runner in output.keys():
        actualOutput.append([runner, durations.formatted(output[runner]["t"])])
    
    return actualOutput





def fetchLeaderboardPlace(runID, category=None):
    if not category:
        category = getCategoryFromRunID(runID)
    if not category:
        return False
    with open(dirPath+"/leaderboardReferences/"+category+".csv", "r") as f:
        reference = list(csv.reader(f))
    runs = [x[0] for x in reference]
    if str(runID) in runs:
        return runs.index(str(runID))+1
    else:
        return False
    
def fetchILPlace(runID):
    level = getLevelFromILID(runID)
    if not level:
        return False
    category = getCategoryFromILID(runID)
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
    cur.execute("SELECT ID FROM tolAccounts WHERE name = ?", (name,))
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
        for runner in output.keys():
            if output[runner]["t"] > currentTime:
                placement += 1
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