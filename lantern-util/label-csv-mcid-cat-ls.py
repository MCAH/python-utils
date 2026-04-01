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

# currently not fully ALW compliant

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

# counts files for progress bar
count = len(glob.glob1(filepath, "*.NEF"))

# !!!! CSV CODE !!!!

# creates new csv
csvname = os.path.join(foldername + '_export-metadata-cat.csv')

with open(os.path.join(filepath, csvname), 'w', encoding='utf-8-sig') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames = ls.catheader)
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

					img.close()
					bar.next()

				except KeyError:

					# variable for path to full jpg files
					jpgname = name + ".jpg"
					jpgpath = os.path.join(directory, jpgname)

					# variable for cropped jpg files
					imgname = name[:-3] + 'img_' + name[-3:]
					imgfilename = imgname + '.jpg'
					imgpath = os.path.join(directory, imgname)

					# sets up default info for all images
					# newrow = {'Record ID': name, 'OCR': ''}
					newrow = {'Record ID': name}

				# !!!! METADATA CODE !!!!

					# checks for text in each field to add to csv, moves on if field is empty
					try:
						head = read['Xmp.photoshop.Headline']
						headline = ' '.join(head.split())
						newrow.update({'Media Title': headline})

					except KeyError: pass

					try:
						loc = read['Xmp.photoshop.City']
						location = ' '.join(loc.split())
						newrow.update({'Location': location})
						
					except KeyError: pass

					try:
						original = read['Xmp.photoshop.Source']
						source = ' '.join(original.split())
						newrow.update({'Source Collection': original})

					except KeyError: pass

					try:
						manufacturer = read['Xmp.photoshop.Instructions']
						newrow.update({'Manufacturer': manufacturer})

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

						newrow.update({'Label Transcription': description})

					except KeyError:
						pass

					# writes row and advances bar
					writer.writerow(newrow)
					img.close()
					bar.next()

	bar.finish()
	print('✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')
