# auth.py
from __future__ import print_function
from googleapiclient.discovery import build 
from google.oauth2 import service_account
import os
dirPath = os.path.dirname(os.path.realpath(__file__))
SCOPES = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]
credentials = service_account.Credentials.from_service_account_file(dirPath+'/sheetsCredentials.json', scopes=SCOPES)
spreadsheet_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)