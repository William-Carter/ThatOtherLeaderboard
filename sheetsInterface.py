import sheetsAuth
import json
import os
dirPath = os.path.dirname(os.path.realpath(__file__))
with open(dirPath+"/config.json") as f:
    sheetID = json.load(f)["leaderboardSheet"]
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


