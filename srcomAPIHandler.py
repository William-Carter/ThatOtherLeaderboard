import os
import requests
import json
dirPath = os.path.dirname(os.path.realpath(__file__))

def getIDFromName(runnerName: str):
    runners = requests.get(f"https://speedrun.com/api/v1/users?name={runnerName}").json()["data"]
    if len(runners) == 0:
        return False
    
    for runner in runners:
        if runner["names"]["international"].lower() == runnerName.lower() or runner["names"]["japanese"] == runnerName:
            return runner["id"]
        

def getNameFromID(runnerID: str):
    with open(dirPath+"/data/runnerNames.json", "r") as f:
        runnerNames = json.load(f)

    if runnerID in runnerNames.keys():
        return runnerNames[runnerID]
    
    else:
        runnerJson = requests.get(f"https://speedrun.com/api/v1/users/{runnerID}").json()
        name = runnerJson["data"]["names"]["international"]
        runnerNames[runnerID] = name

    with open(dirPath+"/data/runnerNames.json", "w") as f:
        json.dump(runnerNames, f)

    return name