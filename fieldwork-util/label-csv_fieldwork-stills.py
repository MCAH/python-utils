import sys
import private_people as people
sys.path.insert(1, '..')
import private
import private_paths as path
import global_var as g
import os
import pyexiv2
import glob
import tkinter as tk
from tkinter import filedialog
from progress.bar import IncrementalBar
import csv
from csv import DictWriter
import re
import argparse
from datetime import datetime

# current version as of jan 22 2025

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
	coll = open('.collection.txt', 'r')
	collection = coll.read()
	coll.close()
	tripterm = open('.trip.txt', 'r')
	trip = tripterm.read()
	tripterm.close()
else:
	filepath = filedialog.askdirectory(
	initialdir = path.default)
	save = open('.filepath.txt', 'w+')
	save.write(filepath)
	save.close()
	collection = input('Collection name:')
	coll = open('.collection.txt', 'w+')
	coll.write(collection)
	coll.close()
	trip = input('MCAH trip:')
	tripterm = open('.trip.txt', 'w+')
	tripterm.write(trip)
	tripterm.close()
root.update()

# prints working directory filepath or just folder name
foldername = os.path.basename(filepath)
# print('Folder: ' + filepath)
print('Folder: ' + foldername)

# counts folders for progress bar
count = 1
for root, dirs, files in os.walk(filepath):
    count += len(dirs)

# !!!! CSV CODE !!!!
 
# creates new csv
csvname = os.path.join(foldername + '_export-metadata_stills.csv')
with open(os.path.join(filepath, csvname), 'w', encoding='utf-8-sig') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames = private.mcidexport)
	writer.writeheader()

	# progress bar setup
	with IncrementalBar('❯', max=count, suffix='%(index)d / %(max)d - %(eta_td)s remaining') as bar:
		for c in range(1):

			for root, dirs, files in os.walk(filepath, topdown=False):
				
				for rawimg in sorted(glob.glob(os.path.join(root, '*.NEF'))):

					if re.search('VR$', root):
						continue
					if re.search('Gigapixel', root):
						continue


					directory, rawfilename = os.path.split(rawimg)
					name, ext = os.path.splitext(rawfilename)

					# variable for path to xmp sidecar
					xmpname = name + ".xmp"
					xmppath = os.path.join(directory, xmpname)

					if 'VR' in xmppath:
						continue
					if 'Gigapixel' in xmppath:
						continue

					# loads file to read metadata
					img = pyexiv2.Image(xmppath)
					read = img.read_xmp()
					exif = img.read_exif()

					# check for imgs to skip
					try:
						# chooses metadata field to read
						label = read['Xmp.xmp.Label']

						# checks to see if image is tagged
						if label == g.red or g.purple:
							continue
						else: continue
					
					except KeyError:

						# variable for path to full jpg files
						jpgname = name + ".jpg"
						jpgpath = os.path.join(directory, jpgname)

						# variable for cropped jpg files
						imgname = name[:-4] + 'img_' + name[-4:]
						imgfilename = imgname + '.jpg'
						imgpath = os.path.join(directory, imgname)

						# checks photographer based on folder name
    					#   i know this can be better but this is it for now
						if re.search('LP', root):
							photog = people.LP
						else:
							photog = people.GR

						# sets up default info for all images
						newrow = {'Media Type': 'Image', 'Media': path.mcid_media + name, 'Thumbnail': path.mcid_thumbnail + jpgname, 'Record ID': name, 'Title':name, 'Photographer': photog, 'Collection': collection, 'Media Source': private.credit, 'MCAH Trip':trip,'Width': '100%', 'Height': '800'}
						
						# !!!! METADATA CODE !!!!

						# checks for text in each field to add to csv, moves on if field is empty
						try:

							works = read['Xmp.dc.title']['lang="x-default"']
							works = works.strip(' |')
							newrow.update({'Media of': works})

						except KeyError: pass

						try:

							description = read['Xmp.dc.description']['lang="x-default"']
							newrow.update({'Media Title': description})

						except KeyError: pass

						try:
							# convert date to preferred format
							date = read['Xmp.exif.DateTimeOriginal']
							year = date[:4]
							date = (datetime.strptime(date[:10], '%Y-%m-%d')).strftime('%d %B, %Y')
							newrow.update({'Media Date': date, 'Media Date Sort': year})

						except KeyError: pass

						try:
							# read and reformat GPS
							# with many many many thanks to https://gist.github.com/chrisjsimpson/076a82b51e8540a117e8aa5e793d06ec

							rawlat = read['Xmp.exif.GPSLatitude']
							rawlong = read['Xmp.exif.GPSLongitude']

							def ddm2dec(dms_str):

								dms_str = re.sub(r'\s', '', dms_str)
								
								sign = -1 if re.search('[swSW]', dms_str) else 1
								
								numbers = [*filter(len, re.split('\D+', dms_str, maxsplit=4))]

								degree = numbers[0]
								minute_decimal = numbers[1] 
								decimal_val = numbers[2] if len(numbers) > 2 else '0' 
								minute_decimal += "." + decimal_val

								return sign * (int(degree) + float(minute_decimal) / 60)

							lat = ddm2dec(rawlat)
							long = ddm2dec(rawlong)
							newrow.update({'Longitude': long, 'Latitude': lat})

						except KeyError: pass

						# writes row and advances bar
						writer.writerow(newrow)
						img.close()
				bar.next()

	bar.finish()
	print('✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')