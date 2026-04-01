import sys
sys.path.insert(0, '..')
import private_paths
import ls
import os
import csv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json
from datetime import *

# current version as of 1 april 2026

# currently only for intial upload

googlecred = private_paths.gcred

# checks for valid token, removes if expired
token = open(googlecred + '/token.json')
tokendata = json.load(token)
expiry = datetime.strptime(tokendata['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ')
today = datetime.now()
if expiry < today:
	os.remove(googlecred + '/token.json')
elif expiry == today:
	os.remove(googlecred + '/token.json')

# # counts files for progress bar
# count = len(glob.glob1(filepath, "*.xmp"))

# !!!! GOOGLE SHEETS API !!!!
# note - need to login with MCAH gmail

# google sheets code from quickstart
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds = None
if os.path.exists(googlecred + '/token.json'):
	creds = Credentials.from_authorized_user_file(
		googlecred + '/token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
	if creds and creds.expired and creds.refresh_token:
		creds.refresh(Request())
	else:
		flow = InstalledAppFlow.from_client_secrets_file(
			googlecred + '/credentials.json', SCOPES)
		creds = flow.run_local_server(port=0)
	# Save the credentials for the next run
	with open(googlecred + '/token.json', 'w') as token:
		token.write(creds.to_json())

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId = private_paths.ls_gsheet, range='Upload!A4:AG').execute()
values = result.get('values', [])
oops = []

for row in values:
		if row[26] != '' and row[30] != '' and row[31] == '':
			batch = row[15]
			drawer = row[0][3:]
			export = os.path.join(private_paths.fp_ls + '/' + batch + '/' + drawer + '/' + drawer + '_export-metadata.csv')

			try:
				with open(export, 'r') as exportcsv:
					next(exportcsv)
					readexport = exportcsv.read()
			except:
				oops.append(batch + ', drawer ' + drawer)
				continue
			else:
				continue

if oops != []:
	print('\nOops! Some export CSVs still need to be generated! (╯°□°)╯︵ ┻━┻\n')
	print(*oops, sep = '\n', end= '\n\n')

# !!!! CSV CODE !!!!
else:
	# creates new csv in temp staging
	with open(os.path.join(private_paths.fp_temp_ls + 'ls_export-metadata.csv'), 'w', encoding='utf-8-sig', newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = ls.tabsheader)
		writer.writeheader()
		csvfile.close()

	with open(os.path.join(private_paths.fp_temp_ls + 'ls_export-metadata.csv'), 'a', encoding='utf-8-sig', newline='') as csvfile:

		# checks google sheet to see what is ready for upload
		for row in values:
			if row[26] != '' and row[30] != '' and row[31] == '':
				batch = row[15]
				drawer = row[0][3:]
				export = os.path.join(private_paths.fp_ls + batch + '/' + drawer + '/' + drawer + '_export-metadata.csv')

				with open(export, 'r') as exportcsv:
					next(exportcsv)
					readexport = exportcsv.read()
					# csvfile.write('\n')
					csvfile.write(readexport)
	
	print('\n✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')