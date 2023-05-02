import databaseManager as dbManager
import srcomAPIHandler
import json
import os
dirPath = os.path.dirname(os.path.realpath(__file__))

insertList = []
for category in ["oob", "inbounds", "unrestricted", "legacy", "glitchless"]:
    print("starting", category)
    with open(dirPath+f"/downloads/{category}DL.json", "r") as f:
        runDL = json.load(f)
    count = 1
    for run in runDL["data"]["runs"]:
        print(count)
        count += 1
        time = run["run"]["times"]["primary_t"]
        date = run["run"]["date"]
        if not date: # Don't accept runs that don't have a valid date. Could also just use current date?
            continue
        runID = run["run"]["id"]
        if "id" in run["run"]["players"][0].keys(): # Don't accept srcom runs from people without an account
            srcomPlayerID = run["run"]["players"][0]["id"]

        else:
            continue

        if not dbManager.srcomAccountTracked(srcomPlayerID):
            playerName = srcomAPIHandler.getNameFromID(srcomPlayerID)
            dbManager.insertSrcomAccount(srcomPlayerID, playerName)

        if not dbManager.runTracked(runID):
            existingRun = dbManager.identicalRunTracked(srcomPlayerID, category, time)
            if existingRun:
                dbManager.addSrcomIDToRun(existingRun, runID)
            else:
                dbManager.insertRun(category, time, date, srcomAccount=srcomPlayerID, srcomID=runID)

        else:
            dbManager.updateSrcomRunTime(runID, time)

            
        
        

