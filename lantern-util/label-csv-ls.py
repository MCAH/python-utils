import sys
sys.path.insert(0, '..')
import private_paths
import ls
import os
from typing import Type
import pyexiv2
import glob
import tkinter as tk
from tkinter import filedialog
from progress.bar import IncrementalBar
import csv
import re
import argparse

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
	filepath = filedialog.askdirectory(initialdir = private_paths.fp_ls)
	save = open('.filepath.txt', 'w+')
	save.write(filepath)
	save.close()
# filepath = filedialog.askdirectory(initialdir = private_paths.fp_ls)
root.update()

# prints working directory filepath or just folder name
foldername = os.path.basename(filepath)
# print('Path: ' + filepath)
print('Folder: ' + foldername)

# counts files for progress bar
count = len(glob.glob1(filepath, "*.NEF"))

# names csv after current folder
csvname = os.path.join(foldername + '_labels.csv')

# creates csv to write
with open(os.path.join(filepath, csvname), 'w', encoding='utf-8-sig') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=ls.workingheader)
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

			# !!!! metadata code !!!!

				# loads file to read metadata
				img = pyexiv2.Image(xmppath)
				read = img.read_xmp()

				newrow = {'filename': name}

				# checks for color label to determine photo type
				try:
					phototag = read['Xmp.xmp.Label']

					if phototag == ls.verso:
						phototype = 'verso'
						newrow.update({'type': phototype})

					elif phototag == ls.reshoot:
						phototype = 'slide'
						newrow.update({'type': phototype})

					elif phototag == ls.reference:
						phototype = 'reference'
						newrow.update({'type': phototype})

					elif phototag == ls.loan:
						phototype = 'loan'
						newrow.update({'type': phototype})

					else:
						phototype = 'tab'
						newrow.update({'type': phototype})

				except KeyError:

					phototype = 'slide'
					newrow.update({'type': phototype})

				# checks for text in other fields to add to csv, moves on if field is empty
				try:
					category = read['Xmp.photoshop.SupplementalCategories']
					subject1 = category[0].replace(',', ', ')
					newrow.update({'s1 LS': subject1})

					try:
						subject2 = category[1].replace(',', ', ')
						newrow.update({'s2 LS': subject2})
					except:
						pass

					try:
						subject3 = category[2].replace(',', ', ')
						newrow.update({'s3 LS': subject3})
					except:
						pass

					try:
						subject4 = category[3].replace(',', ', ')
						newrow.update({'s4 LS': subject4})
					except:
						pass

					try:
						subject5 = category[4].replace(',', ', ')
						newrow.update({'s5 LS': subject5})
					except:
						pass

					try:
						subject6 = category[5].replace(',', ', ')
						newrow.update({'s6 LS': subject6})
					except:
						pass
  
					try:
						subject7 = category[6].replace(',', ', ')
						newrow.update({'s7 LS': subject7})
					except:
						pass

				except KeyError: pass

				try:
					subhead = read['Xmp.photoshop.Category']
					subheading = subhead.replace(',', ', ')
					newrow.update({'subheading': subheading})

				except KeyError: pass
				
				try:
					try: caption = read['Xmp.dc.description']['lang="x-default"']
					except: caption = read['Xmp.dc.description']

					# removes non-latin characters (likely OCR errors) and convert to string
					latintxt = [t for t in caption if not re.findall(
						"[^\u0000-\u017F]+", t)]
					filteredtxt = ''.join(latintxt)

					# removes empty delimiters and clear remaining whitespace for final caption format
					cleantxt = filteredtxt.replace(' ;', '')
					transcription = ' '.join(cleantxt.split())

					newrow.update({'transcription': transcription})

				except KeyError: pass

				try:
					headline = read['Xmp.photoshop.Headline']
					newrow.update({'title': headline})

				except KeyError: pass

				try:
					location = read['Xmp.photoshop.City']
					newrow.update({'location': location})
				
				except KeyError: pass
				
				try:
					manufacturer = read['Xmp.photoshop.Instructions']
					newrow.update({'manufacturer': manufacturer})

				except KeyError: pass

				try:
					source = read['Xmp.photoshop.Source']
					newrow.update({'source': source})

				except KeyError: pass

				try:
					verso = read['Xmp.photoshop.CaptionWriter']
					newrow.update({'verso': verso})

				except KeyError: pass

				try:
					rating = read['Xmp.xmp.Rating']
					if rating == '5':
						newrow.update({'attribute': 'hand'})
					if rating == '4':
						newrow.update({'attribute': 'film'})
					if rating == '3':
						newrow.update({'attribute': 'auto'})

				except KeyError: pass

				# writes row and advances bar
				writer.writerow(newrow)
				img.close()
				bar.next()

	bar.finish()
	print('✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')
