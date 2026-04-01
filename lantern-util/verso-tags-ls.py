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
count = len(glob.glob1(filepath, '*.NEF'))

# sets variables for loops
vfilename = ''

with IncrementalBar('Progress:', max=count, suffix='%(index)d / %(max)d - %(eta_td)s remaining') as bar:
    for c in range(1):

        # verso check for consecutive versos before renaming images REVERSED
        for rawpath in reversed(sorted(glob.glob(os.path.join(filepath, '*.NEF')))):
                    directory, rawfilename = os.path.split(rawpath)
                    name, ext = os.path.splitext(rawfilename)

                    # variable for path to xmp sidecar
                    xmpname = name + ".xmp"
                    xmppath = os.path.join(directory, xmpname)

                # !!!! metadata code !!!!

                    # loads file to read metadata
                    img = pyexiv2.Image(xmppath)
                    read = img.read_xmp()

                    try:
                        # chooses metadata field to read
                        label = read['Xmp.xmp.Label']

                        # checks to see if image is tagged as verso

                        if label == ls.verso:
                            rating = read['Xmp.xmp.Rating']
                            if rating == '1':
                                vfilename = name
                        
                            bar.next()

                        # checks if image is tagged but not as verso
                        elif label != ls.verso:
                            
                            metadata = {'Xmp.photoshop.CaptionWriter': vfilename}
                            img.modify_xmp(metadata)
                            img.close()
                            vfilename = ''
                            bar.next()

                    # error checks for blank tag indicating front of card
                    except KeyError:
                            
                        metadata = {'Xmp.photoshop.CaptionWriter': vfilename}
                        img.modify_xmp(metadata)
                        img.close()
                        vfilename = ''
                        bar.next()

bar.finish()
    
# print('generate new CSV?? (y/n)')
# answer = input().lower().strip()
# if answer == 'y':
#     # print('\n')
#     exec(open('label-csv-ls.py').read())

# else: 
#     print('\n✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')