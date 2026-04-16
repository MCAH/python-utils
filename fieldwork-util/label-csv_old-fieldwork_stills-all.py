# current version as of 16 april 2026

# quick & dirty script to export fieldwork stills that were cataloged in the old way on lightroom. assumes:
# headline = view description
# sublocation = title
# city = location

# will output metadata for RAW and JPG but should not duplicate in the case of raw+jpg

import sys
sys.path.insert(0, '..')
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
    filepath = filedialog.askdirectory(
    initialdir = path.default)
    save = open('.filepath.txt', 'w+')
    save.write(filepath)
    save.close()
root.update()

# prints working directory filepath or just folder name
foldername = os.path.basename(filepath)
# print('Folder: ' + filepath)
print('Folder: ' + foldername)

# counts folders for progress bar
count = 1
for root, dirs, files in os.walk(filepath):
    count += len(dirs)

pyexiv2.set_log_level(4)

# !!!! FUNCTIONS !!!

skip = ['VR', 'Pano', ' Gigapixel', 'Photogram', 'photogram']

def RAWimg():
    directory, rawfilename = os.path.split(rawimg)
    name, ext = os.path.splitext(rawfilename)

    # variable for path to xmp sidecar
    xmpname = name + ".xmp"
    xmppath = os.path.join(directory, xmpname)

    if any(word in skip for word in xmppath):
        return

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
            return
        else:
            return

    except KeyError:

        # sets up default info for all images
        newrow = {'Media Type': 'Image','Record ID': name, 'Folder': directory}

        # !!!! METADATA CODE !!!!

        # checks for text in each field to add to csv, moves on if field is empty
        try:

            # description = read['Xmp.dc.description']['lang="x-default"']
            description = read['Xmp.photoshop.Headline']
            newrow.update({'old view description': description})

        except KeyError:
            pass

        try:
            sublocation = read['Xmp.iptc.Location']
            newrow.update({'old title': sublocation})

        except KeyError: pass

        try:

            city = read['Xmp.photoshop.City']
            newrow.update({'old location': city})

        except KeyError: pass

        try:
            # convert date to preferred format
            date = read['Xmp.exif.DateTimeOriginal']
            year = date[:4]
            date = (datetime.strptime(date[:10], '%Y-%m-%d')).strftime('%d %B, %Y')
            newrow.update({'Media Date': date, 'Media Date Sort': year})

        except KeyError:
            pass

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

        except KeyError:
            pass

        # writes row and advances bar
        writer.writerow(newrow)
        img.close()

def JPGimg():

    # image set up
    directory, rawfilename = os.path.split(rawimg)

    if any(word in skip for word in directory):
        return

    name, ext = os.path.splitext(rawfilename)

    # skips raw + jpg
    arwname = name + ".ARW"
    arwpath = os.path.join(directory, arwname)
    if os.path.isfile(arwpath):
        return

    # loads file to read metadata
    img = pyexiv2.Image(rawimg)
    read = img.read_xmp()

    # check for imgs to skip
    try:
        # chooses metadata field to read
        label = read['Xmp.xmp.Label']

        # checks to see if image is tagged
        if label == g.red or g.purple:
            return
        else:
            return

    except KeyError:

        # sets up default info for all images
        newrow = {'Media Type': 'Image','Record ID': name, 'Folder': foldername}

        # !!!! METADATA CODE !!!!

        # checks for text in each field to add to csv, moves on if field is empty
        try:

            # description = read['Xmp.dc.description']['lang="x-default"']
            description = read["Xmp.photoshop.Headline"]
            newrow.update({'old view description': description})

        except KeyError:
            pass

        try:
            sublocation = read['Xmp.iptc.Location']
            newrow.update({'old title': sublocation})

        except KeyError: pass

        try:

            city = read['Xmp.photoshop.City']
            newrow.update({'old location': city})

        except KeyError: pass

        try:
            # convert date to preferred format
            date = read["Xmp.xmp.CreateDate"]
            year = date[:4]
            date = (datetime.strptime(date[:10], "%Y-%m-%d")).strftime("%d %B, %Y")
            newrow.update({"Media Date": date, "Media Date Sort": year})

        except KeyError:
            pass

        try:
            # read and reformat GPS
            # with many many many thanks to https://gist.github.com/chrisjsimpson/076a82b51e8540a117e8aa5e793d06ec

            rawlat = read["Xmp.exif.GPSLatitude"]
            rawlong = read["Xmp.exif.GPSLongitude"]

            def ddm2dec(dms_str):

                dms_str = re.sub(r"\s", "", dms_str)

                sign = -1 if re.search("[swSW]", dms_str) else 1

                numbers = [*filter(len, re.split("\D+", dms_str, maxsplit=4))]

                degree = numbers[0]
                minute_decimal = numbers[1]
                decimal_val = numbers[2] if len(numbers) > 2 else "0"
                minute_decimal += "." + decimal_val

                return sign * (int(degree) + float(minute_decimal) / 60)

            lat = ddm2dec(rawlat)
            long = ddm2dec(rawlong)
            newrow.update({"Longitude": long, "Latitude": lat})

        except KeyError:
            pass

        # writes row and advances bar
        writer.writerow(newrow)
        img.close()

# !!!! CSV CODE !!!!

header = {'Media Type','Record ID', 'Folder', 'old view description', 'old title', 'old location', 'Media Date', 'Media Date Sort', 'Longitude', 'Latitude'}

# creates new csv
csvname = os.path.join(foldername + '_export-metadata_stills-all.csv')
with open(os.path.join(filepath, csvname), 'w', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = header)
    writer.writeheader()

    # progress bar setup
    with IncrementalBar('❯', max=count, suffix='%(index)d / %(max)d - %(eta_td)s remaining') as bar:
        for c in range(1):

            for root, dirs, files in os.walk(filepath, topdown=False):

                for rawimg in sorted(glob.glob(os.path.join(root, '*.ARW'))):

                    RAWimg()

                for rawimg in sorted(glob.glob(os.path.join(root, '*.NEF'))):

                    RAWimg()

                for rawimg in sorted(glob.glob(os.path.join(root, "*.JPG"))):

                    JPGimg()

                bar.next()

    bar.finish()
    print('✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')
