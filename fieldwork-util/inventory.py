#!/usr/bin/python
# initial source: https://gist.github.com/Grimthorr/8ea07f43cebeb4156e54

import sys
sys.path.insert(1, ".")
import private_paths as path
import os
import tkinter as tk
from tkinter import filedialog
import argparse

# current version as of 13 Nov 2025

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
    filepath = filedialog.askdirectory(initialdir = path.default)
    save = open(".filepath.txt", "w+")
    save.write(filepath)
    save.close()
root.update()

outputfile	=  os.path.join(filepath, 'filename-inventory.txt')

exclude		= ['Thumbs.db','.tmp','.DS_Store','filename-inventory.txt', '.afpDeleted']	# exclude files containing these strings
pathsep		= "/"			# path separator ('/' for linux, '\' for Windows)
# end editable vars #

with open(outputfile, "w") as txtfile:
	for path,dirs,files in os.walk(filepath):

		# commented out - separate fields by subfolder. makes easier to read
		
		# sep = "\n---------- " + path.split(pathsep)[len(path.split(pathsep))-1] + " ----------"
		# txtfile.write("%s\n" % sep)

		for fn in sorted(files):
			if not any(x in fn for x in exclude):
				filename = os.path.splitext(fn)[0]
				txtfile.write("%s\n" % filename)
txtfile.close()
print('✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')
