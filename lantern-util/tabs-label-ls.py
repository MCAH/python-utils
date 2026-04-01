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
import argparse
from titlecase import titlecase

# current version as of 31 march 2026

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
count = len(glob.glob1(filepath, '*.NEF'))

# sort because tabs are behind images
sort = reversed(sorted(glob.glob(os.path.join(filepath, '*.NEF'))))

# set up for loop
sub1 = sub2 = sub3 = sub4 = sub5 = subhead = ''
metadata = []

def writeall():
	# writes all tabs to metadata
	metadata.extend((sub1, sub2, sub3, sub4, sub5, subhead))
	img.modify_xmp(
		{'Xmp.photoshop.SupplementalCategories': metadata})
	img.close()

	# advance bar
	bar.next()

# progress bar setup
with IncrementalBar('Progress:', max=count, suffix='%(index)d / %(max)d - %(eta_td)s remaining') as bar:
	for c in range(1):

		# isolates NEF filename and path for use with other file types; sorts by filename REVERSED
		for rawpath in sort:
			directory, rawfilename = os.path.split(rawpath)
			name, ext = os.path.splitext(rawfilename)

			# variable for path to xmp sidecar
			xmpname = name + ".xmp"
			xmppath = os.path.join(directory, xmpname)

		# !!!! metadata code !!!!

			# loads file to read metadata
			img = pyexiv2.Image(xmppath)
			read = img.read_xmp()

			# clears last image tags
			metadata.clear()

			try:
				# chooses metadata field to read
				label = read['Xmp.xmp.Label']

				# checks to see if image is tagged as verso
				if label == ls.red:

					# reads tab text from metadata & collapse commas
					sub1 = read['Xmp.dc.description']['lang="x-default"']

					sub1raw = titlecase(sub1.upper(), callback=ls.exceptions)
					print(sub1raw)
					sub1 = sub1raw.strip(';, \t\n\r')
					
					# check if subheading exists
					try:
						subhead = read['Xmp.photoshop.Headline']
						subheadraw = titlecase(subhead.upper(), callback=ls.exceptions)
						subhead = subheadraw.strip(';, \t\n\r')
						subhead = subhead.replace(', ', ',').replace(' ,', ',')

					except KeyError:
						subhead = ''
					
					img.close()
					sub1 = sub1.replace(', ', ',').replace(' ,', ',')

					# resets descriptions of all tabs below in hierarchy
					sub2 = sub3 = sub4 = sub5 = ''

					# advance bar
					bar.next()

				elif label == ls.green:

					# reads tab text from metadata & collapse commas
					sub2 = read['Xmp.dc.description']['lang="x-default"']
					img.close()

					sub2raw = titlecase(sub2.upper(), callback=ls.exceptions)
					sub2 = sub2raw.strip(';, \t\n\r')
					sub2 = sub2.replace(', ', ',').replace(' ,', ',')

					# resets descriptions of all tabs below in hierarchy
					sub3 = sub4 = sub5 = ''

					# advance bar
					bar.next()

				elif label == ls.yellow:

					# reads tab text from metadata & collapse commas
					sub3 = read['Xmp.dc.description']['lang="x-default"']
					img.close()

					sub3raw = titlecase(sub3.upper(), callback=ls.exceptions)
					sub3 = sub3raw.strip(';, \t\n\r')
					sub3 = sub3.replace(', ', ',').replace(' ,', ',')

					# resets descriptions of all tabs below in hierarchy
					sub4 = sub5 = ''

					# advance bar
					bar.next()

				elif label == ls.blue:

					# reads tab text from metadata & collapse commas
					sub4 = read['Xmp.dc.description']['lang="x-default"']
					img.close()

					sub4raw = titlecase(sub4.upper(), callback=ls.exceptions)
					sub4 = sub4raw.strip(';, \t\n\r')
					sub4 = sub4.replace(', ', ',').replace(' ,', ',')

					sub5 = ''

					# advance bar
					bar.next()

				elif label == ls.white:

					# reads tab text from metadata & collapse commas
					sub5 = read['Xmp.dc.description']['lang="x-default"']
					img.close()

					sub5raw = titlecase(sub5.upper(), callback=ls.exceptions)
					sub5 = sub5raw.strip(';, \t\n\r')
					sub5 = sub5.replace(', ', ',').replace(' ,', ',')

					# advance bar
					bar.next()

				elif label == ls.verso or ls.verso2 or ls.reshoot or ls.loan or ls.reference: writeall()

				else: bar.next()

			# error checks for blank tag indicating front of card
			except KeyError: writeall()

bar.finish()

print('updating CSV\n')

if args.last:
	exec(open('label-csv-ls.py').read())
else:
	os.system('python3 label-csv-ls.py -l')