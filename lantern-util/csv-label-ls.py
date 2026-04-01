import sys
sys.path.insert(0, '..')
import private_paths
import os
import pyexiv2
import glob
import tkinter as tk
from tkinter import filedialog
from progress.bar import IncrementalBar
import csv
from csv import DictReader
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

# opens csv
with open(os.path.join(filepath, csvname), 'r', encoding='utf-8-sig') as csvfile:
	reader = csv.DictReader(csvfile)

	# progress bar setup
	with IncrementalBar('Progress:', max=count, suffix='%(index)d / %(max)d - %(eta_td)s remaining') as bar:
		for c in range(1):

			# iterates thru csv
			for row in reader:

				# isolates NEF filename and path for use with other file types
				for rawimg in glob.glob(os.path.join(filepath, '*.NEF')):
					directory, rawfilename = os.path.split(rawimg)
					name, ext = os.path.splitext(rawfilename)

					# variable for path to xmp sidecar
					xmpname = name + ".xmp"
					xmppath = os.path.join(directory, xmpname)

					if row['filename'] == name:

						# loads file to read metadata
						img = pyexiv2.Image(xmppath)
						read = img.read_xmp()
						# data = img.read_iptc()

						# writes subjects
						if row['s1 LS'] == '':
							subjects = ''
						else:
							subject1 = row['s1 LS'].replace(', ', ',')
								
							if row['s2 LS'] == '':
								subjects = subject1
							else:
								subject2 = row['s2 LS'].replace(
									', ', ',')

								if row['s3 LS'] == '':
									subjects = subject1 + ', ' + subject2
								else:
									subject3 = row['s3 LS'].replace(
										', ', ',')
									
									if row['s4 LS'] == '':
										subjects = subject1 + ', ' + subject2 + ', ' + subject3
									else:
										subject4 = row['s4 LS'].replace(', ', ',')

										if row['s5 LS'] == '':
											subjects = subject1 + ', ' + subject2 + ', ' + subject3 + ', ' + subject4
										else:
											subject5 = row['s5 LS'].replace(
												', ', ',')

											if row['s6 LS'] == '':
												subjects = subject1 + ', ' + subject2 + ', ' + subject3 + ', ' + subject4 + ', ' + subject5
											else:
												subject6 = row['s6 LS'].replace(
													', ', ',')

												if row['s7 LS'] == '':
													subjects = subject1 + ', ' + subject2 + ', ' + subject3 + ', ' + subject4 + ', ' + subject5 + ', ' + subject6
												else:
													subject7 = row['s7 LS'].replace(
														', ', ',')
													subjects = subject1 + ', ' + subject2 + ', ' + subject3 + ', ' + subject4 + ', ' + subject5 + ', ' + subject6 + ', ' + subject7

						# defines fields to add to metadata and clear old caption
						metadata = { 'Xmp.dc.description': row['transcription'], 'Xmp.photoshop.Headline': row['title'], 'Xmp.photoshop.City': row['location'], 'Xmp.photoshop.CaptionWriter': row['verso'], 'Xmp.photoshop.SupplementalCategories': subjects, 'Xmp.photoshop.Instructions': row['manufacturer'], 'Xmp.photoshop.Source': row['source'], 'Xmp.photoshop.Category': row['subheading']}

						# writes metadata
						img.modify_xmp(metadata)
						img.close()

						# advance bar
						bar.next()

	bar.finish()
	print('✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')
