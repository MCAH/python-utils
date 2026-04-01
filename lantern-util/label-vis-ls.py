import sys
sys.path.insert(0, '..')
import private_paths
import ls
import rawpy
import imageio
import io
import os
import pyexiv2
import glob
import tkinter as tk
from tkinter import filedialog
import pathlib
from progress.bar import IncrementalBar
import csv
import re
import argparse
import cv2

# current version as of 1 april 2026

# set path to google credentials json for access
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = private_paths.gcred + 'gvis.json'

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

# names csv after current folder
csvname = os.path.join(foldername + '_labels.csv')

# list of terms/strings to ignore on labels (case-sensitive)
ignore = ['COLUMBIA UNIVERSITY', 'DEPARTMENT OF FINE ARTS AND ARCHAEOLOGY']

# creates csv to write & sets csv header
with open(os.path.join(filepath, csvname), 'w', encoding='utf-8-sig') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames = ls.workingheader)
	writer.writeheader()

	# progress bar setup
	with IncrementalBar('Progress:', max=count, suffix='%(index)d / %(max)d - %(eta_td)s remaining') as bar:
		for c in range(1):

			# isolates NEF filename and path for use with other file types
			for rawimg in sorted(glob.glob(os.path.join(filepath, '*.NEF'))):
				directory, rawfilename = os.path.split(rawimg)
				name, ext = os.path.splitext(rawfilename)

				# variable for path to raw image
				rawpath = os.path.join(directory, rawfilename)

				# variable for path to jpg image
				jpgname = name + ".jpg"
				jpgpath = os.path.join(directory, jpgname)

				# variable for path to xmp sidecar
				xmpname = name + ".xmp"
				xmppath = os.path.join(directory, xmpname)

				newrow = {'filename': name}

				# checks if xmp files have already been generated
				xmpcheck = pathlib.Path(xmppath)
				if xmpcheck.exists():

					# converts raw image to jpg
					with rawpy.imread(rawpath) as raw:
						rgb = raw.postprocess(half_size=True)
					imageio.imsave(jpgpath, rgb, quality=20)

					# rotates jpg copy 180 for theoretically better ocr results
					jpg0 = cv2.imread(jpgpath)
					jpg180 = cv2.rotate(jpg0, cv2.ROTATE_180)
					cv2.imwrite(jpgpath, jpg180)

				# !!!! google vis / ocr code !!!!

					# Imports the Google Cloud client library
					from google.cloud import vision

					# Instantiates a client
					client = vision.ImageAnnotatorClient()

					# The name of the image file to annotate
					file_name = os.path.abspath(jpgpath)

					# Loads the image into memory
					with io.open(file_name, 'rb') as image_file:
						content = image_file.read()

					image = vision.Image(content=content)

					# Performs label detection on the image file
					response = client.document_text_detection(image=image)
					texts = response.text_annotations

				# !!!! caption writing code !!!!

					# checks to ensure image has text before trying to write to metadata
					if texts == '':

						# writes row, deletes jpg & advance bar
						writer.writerow(newrow)
						os.remove(jpgpath)
						bar.next()
						continue

					else:
						for text in texts:
							rawtxt = text.description
							break

						# removes terms as specified above
						for i in ignore:
							rawtxt = rawtxt.replace(i, '')

						# removes non-latin characters (likely OCR errors) and convert to string
						latintxt = [t for t in rawtxt if not re.findall(
							"[^\u0000-\u017F]+", t)]
						filteredtxt = ''.join(latintxt)

						# removes empty lines and trailing spaces
						compacttxt = ''.join(
							[s for s in filteredtxt.strip().splitlines(True) if s.strip()])

						# replaces line break with delimiter and removes empty delimiters
						cleantxt = compacttxt.replace('\n', '; ')
						extracleantxt = cleantxt.replace(' ;', '')

						# clears any leftover whitespace for final caption format
						caption = ' '.join(extracleantxt.split())

					# !!!! metadata code !!!!

						# loads file to read metadata
						img = pyexiv2.Image(xmppath)
						read = img.read_xmp()

						# defines fields to add to metadata
						metadata = {'Xmp.dc.description': caption}

						# writes metadata
						img.modify_xmp(metadata)

						# writes csv row
						newrow.update({'transcription': caption})

					try:
						phototag = read['Xmp.xmp.Label']

						if phototag == ls.verso:
							phototype = 'verso'

						else:
							phototype = 'tab'
							newrow.update({'type': phototype})
							img.close()

					except KeyError:

						phototype = 'photograph'
						newrow.update({'type': phototype})
						img.close()

					# deletes jpg & advance bar
					writer.writerow(newrow)
					os.remove(jpgpath)
					bar.next()

				# terminates script if no XMP file found for an image
				else:
					print('\n\nXMP files need to be generated for this folder!')
					quit()
bar.finish()
print('✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')
