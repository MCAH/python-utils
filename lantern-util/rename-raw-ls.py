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
lastfront = lastverso = ''
start = refstart = num = lastversonum = 0
doubles = []

# verso check for consecutive versos before renaming images
for rawpath in sorted(glob.glob(os.path.join(filepath, '*.NEF'))):
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

                    # assigns image number
                    num += 1

                    # checks to see if last image number and current are consecutive
                    versocheck = [lastversonum, num]
                    def check(l):
                        return sorted(l) == list(range(min(l), max(l)+1))
                    # if consecuitve appends to list
                    if check(versocheck) == True:
                        doubles.append(lastverso + ' + ' + name)

                    # sets variable for next loop
                    lastverso = name
                    lastversonum = num
                    img.close()

                # checks if image is tagged but not as verso
                elif label != ls.verso:

                    # assigns image number
                    num += 1
                    img.close()

            # error checks for blank tag indicating front of card
            except KeyError:

                # assigns image number
                num += 1
                img.close()

# if no issues, continues to rename images
if doubles == []:
    print('No consecutive versos found!')

    # progress bar setup
    with IncrementalBar('Progress:', max=count, suffix='%(index)d / %(max)d - %(eta_td)s remaining') as bar:
        for c in range(1):

            # isolates NEF filename and path for use with other file types; sorts by filename
            for rawpath in sorted(glob.glob(os.path.join(filepath, '*.NEF'))):
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

                        # sets new filename based on last card front record id
                        versoname = '2224_lantern_' + foldername + '_' + photonumber + 'v'
                        versorawname = versoname + '.NEF'
                        versoxmpname = versoname + '.xmp'

                        # sets path and renames
                        versorawpath = os.path.join(directory, versorawname)
                        versoxmppath = os.path.join(directory, versoxmpname)
                        os.rename(rawpath, versorawpath)
                        os.rename(xmppath, versoxmppath)

                        # advance bar
                        img.close()
                        bar.next()

                    elif label == ls.reshoot:

                        # adds 1 to record id number
                        start += 1
                        number = str(start)
                        photonumber = number.zfill(3)

                        # creates new record id
                        lastfront = '2224_lantern_' + foldername + '_' + photonumber
                        rectorawname = lastfront + '.NEF'
                        rectoxmpname = lastfront + '.xmp'

                        # sets path and renames
                        rectorawpath = os.path.join(directory, rectorawname)
                        rectoxmppath = os.path.join(directory, rectoxmpname)
                        os.rename(rawpath, rectorawpath)
                        os.rename(xmppath, rectoxmppath)

                        # advance bar
                        img.close()
                        bar.next()

                    elif label == ls.loan:

                        # adds 1 to record id number
                        start += 1
                        number = str(start)
                        photonumber = number.zfill(3)

                        # creates new record id
                        lastfront = '2224_lantern_' + foldername + '_' + photonumber + '_loan'
                        rectorawname = lastfront + '.NEF'
                        rectoxmpname = lastfront + '.xmp'

                        # sets path and renames
                        rectorawpath = os.path.join(directory, rectorawname)
                        rectoxmppath = os.path.join(directory, rectoxmpname)
                        os.rename(rawpath, rectorawpath)
                        os.rename(xmppath, rectoxmppath)

                        # advance bar
                        img.close()
                        bar.next()

                    elif label == ls.reference:

                        # adds 1 to record id number
                        refstart += 1
                        number = str(refstart)
                        refnumber = number.zfill(3)

                        # creates new record id
                        lastfront = '2224_lantern_' + foldername + '_ref_' + refnumber
                        refrawname = lastfront + '.NEF'
                        refxmpname = lastfront + '.xmp'

                        # sets path and renames
                        refrawpath = os.path.join(directory, refrawname)
                        refxmppath = os.path.join(directory, refxmpname)
                        os.rename(rawpath, refrawpath)
                        os.rename(xmppath, refxmppath)

                        lastfront = lastfront

                        # advance bar
                        img.close()
                        bar.next()
                    
                    # checks if image is tagged but not as verso, reference, or reshoot
                    else:

                        lastfront = lastfront

                        # advance bar
                        img.close()
                        bar.next()

                # error checks for blank tag indicating front of card
                except KeyError:

                    # adds 1 to record id number
                    start += 1
                    number = str(start)
                    photonumber = number.zfill(3)

                    # creates new record id
                    lastfront = '2224_lantern_' + foldername + '_' + photonumber
                    rectorawname = lastfront + '.NEF'
                    rectoxmpname = lastfront + '.xmp'

                    # sets path and renames
                    rectorawpath = os.path.join(directory, rectorawname)
                    rectoxmppath = os.path.join(directory, rectoxmpname)
                    os.rename(rawpath, rectorawpath)
                    os.rename(xmppath, rectoxmppath)

                    # advance bar
                    img.close()
                    bar.next()

    bar.finish()

    print('connecting versos to upload\n')
    exec(open('verso-tags-ls.py').read())
    print('updating CSV\n')
    exec(open('label-csv-ls.py').read())
    
    # print('generate new CSV?? (y/n)')
    # answer = input().lower().strip()
    # if answer == 'y':
    #     # print('\n')
    #     exec(open('label-csv-ls.py').read())

    # else: 
	#     print('\n✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')

# if issues, prints list of consecutive versos to terminal
else:
    print('\nConsecutive versos found! (╯°□°)╯︵ ┻━┻\n')
    print(*doubles, sep = '\n', end= '\n\n')