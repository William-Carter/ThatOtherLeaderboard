import sheetsAuth
import json
import os
import time
import asyncio
dirPath = os.path.dirname(os.path.realpath(__file__))
with open(dirPath+"/config.json") as f:
    e = json.load(f)
    sheetID = e["leaderboardSheet"]
    ILID = e["ILBoardSheet"]

def writeLeaderboard(sheetName: str, values: list):
    spreadsheet_id = sheetID
    rows = len(values)
    range_name = sheetName+"!B2:C"+str(rows+2)
    value_input_option = 'USER_ENTERED'
    body = {
        'values': values
    }
    result = sheetsAuth.spreadsheet_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))


def writeIlBoard(sheetName: str, category: str, values: list):
    ranges = {"glitchless": "!B4:C",
              "inbounds": "!F4:G",
              "oob": "!J4:K"}
    spreadsheet_id = ILID
    rows = len(values)
    range_name = sheetName+ranges[category]+str(rows+4)
    value_input_option = 'USER_ENTERED'
    body = {
        'values': values
    }
    try:
        result = sheetsAuth.spreadsheet_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    except:
        return "failed"
    
    print('{0} cells updated.'.format(result.get('updatedCells')))
    return "success"


    