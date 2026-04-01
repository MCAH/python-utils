import sys
sys.path.insert(0, '..')
import private_paths
import ls
import os
import pyexiv2
import glob
import tkinter as tk
from tkinter import filedialog
from progress.bar import IncrementalBar
import csv
from csv import DictWriter
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import argparse
import json
import re
from datetime import *

# current version as of 1 april 2026

# select working directory
root = tk.Tk()
root.withdraw()
parser = argparse.ArgumentParser()
parser.add_argument('-last', '-l', action='store_true')
args = parser.parse_args()
if args.last:
	save = open('.filepath.txt', 'r')
	filepath = save.read()
	save.close()
else:
	filepath = filedialog.askdirectory(initialdir = private_paths.fp_lantern)
	save = open('.filepath.txt', 'w+')
	save.write(filepath)
	save.close()
# filepath = filedialog.askdirectory(initialdir = private_paths.fp_lantern)
root.update()

# prints working directory filepath or just folder name
foldername = os.path.basename(filepath)
# print('Path: ' + filepath)
print('Folder: ' + foldername)

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

# counts files for progress bar
count = len(glob.glob1(filepath, "*.xmp"))

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
result = sheet.values().get(spreadsheetId=private_paths.ls_gsheet,
							range='Digitization!A4:W').execute()
values = result.get('values', [])

# searches google sheet to pull digitized date
for row in values:
	if row[0][3:] == foldername:
		digdate = '20' + row[20][:2]
		drawer = row[0]

# !!!! CSV CODE !!!!
# creates new csv
csvname = os.path.join(foldername + '_export-metadata.csv')

with open(os.path.join(filepath, csvname), 'w', encoding='utf-8-sig') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames = ls.tabsheader)
	writer.writeheader()

	# progress bar setup
	with IncrementalBar('Progress:', max=count, suffix='%(index)d / %(max)d - %(eta_td)s remaining') as bar:
		for c in range(1):

			# isolates NEF filename and path for use with other file types
			for rawimg in sorted(glob.glob(os.path.join(filepath, '*.NEF'))):
				directory, rawfilename = os.path.split(rawimg)
				name, ext = os.path.splitext(rawfilename)

				# variable for path to xmp sidecar
				xmpname = name + ".xmp"
				xmppath = os.path.join(directory, xmpname)

				# loads file to read metadata
				img = pyexiv2.Image(xmppath)
				read = img.read_xmp()

				# error checks for blank label indicating front of card
				try:
					label = read['Xmp.xmp.Label']

				except KeyError:

					# variable for path to full jpg files
					jpgname = name + ".jpg"
					jpgpath = os.path.join(directory, jpgname)

					# variable for cropped jpg files
					imgname = name[:-3] + 'img_' + name[-3:]
					imgfilename = imgname + '.jpg'
					imgpath = os.path.join(directory, imgname)

					# sets up concatenation for MCID
					media = private_paths.mcid_media + name
					thumbnail = private_paths.mcid_thumbnail + jpgname
					drawername = 'LS_' + foldername

					# sets up default info for all images
					newrow = {'Media Type': 'Lantern Slide', 'Record ID': name, 'Media': media, 'Thumbnail': thumbnail, 'Media Source': 'lantern-slides', 'Digitized Date': digdate, 'Storage Location': drawername, 'Collection': private_paths.ls_collection, 'MCAH Project/Trip': private_paths.ls_project, 'ALW Complete': 'true'}

				# !!!! METADATA CODE !!!!

					# checks for text in each field to add to csv, moves on if field is empty
					try:
						category = read['Xmp.photoshop.SupplementalCategories']
						subject1 = category[0].replace(',', ', ')
						newrow.update({'s1 LS': subject1})

						try:
							subject2 = category[1].replace(',', ', ')
							newrow.update({'s2 LS': subject2})
						except: pass

						try:
							subject3 = category[2].replace(',', ', ')
							newrow.update({'s3 LS': subject3})
						except: pass

						try:
							subject4 = category[3].replace(',', ', ')
							newrow.update({'s4 LS': subject4})
						except: pass

						try:
							subject5 = category[4].replace(',', ', ')
							newrow.update({'s5 LS': subject5})
						except: pass

						try:
							subject6 = category[5].replace(',', ', ')
							newrow.update({'s6 LS': subject6})
						except: pass
	
						try:
							subject7 = category[6].replace(',', ', ')
							newrow.update({'s7 LS': subject7})
						except: pass

					except KeyError: pass

					try:
						subhead = read['Xmp.photoshop.Category']
						subheading = subhead.replace(',', ', ')
						newrow.update({'Subheading': subheading})

					except KeyError: pass

					try:
						original = read['Xmp.photoshop.Source']
						newrow.update({'Source Collection': original})

					except KeyError:
						pass

					try:
						manufacturer = read['Xmp.photoshop.Instructions']
						newrow.update({'Manufacturer': manufacturer})

					except KeyError: pass

					try:
						verso = read['Xmp.photoshop.CaptionWriter']
						if verso != '':
							newrow.update({'Verso Media': verso, 'Verso Thumbnail': (private_paths.mcid_thumbnail + verso + '.jpg')})

					except KeyError: pass

					try:
						rating = read['Xmp.xmp.Rating']
						if rating == '5':
							newrow.update({'Slide Attribute': 'hand-colored'})
						elif rating == '4':
							newrow.update({'Slide Attribute': 'color film'})
						elif rating == '3':
							newrow.update({'Slide Attribute': 'Autochrome'})

					except KeyError: pass

					try:
						caption = read['Xmp.dc.description']['lang="x-default"']

						# removes non-latin characters (likely OCR errors) and convert to string
						latintxt = [t for t in caption if not re.findall(
							"[^\u0000-\u017F]+", t)]
						filteredtxt = ''.join(latintxt)

						# removes empty delimiters and clear remaining whitespace for final caption format
						cleantxt = filteredtxt.replace(' ;', '')
						description = ' '.join(cleantxt.split())

						newrow.update({'OCR Description': description})

					except KeyError:
						pass

					# writes row and advances bar
					writer.writerow(newrow)
					img.close()
					bar.next()

	bar.finish()
	print('✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')
