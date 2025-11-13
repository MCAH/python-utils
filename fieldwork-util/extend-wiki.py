import sys
sys.path.insert(0, '..')
import private
import private_paths as path
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename
import csv
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config as wbi_config

# current version as of 13 Nov 2025

# select working directory
root = tk.Tk()
root.withdraw()
filename = askopenfilename(initialdir=path.default)
directory = os.path.split(filename)[0]

wbi_config["USER_AGENT"] = private.wikiuser
wbi = WikibaseIntegrator()

# filename = "csv.csv"
newcsv = os.path.join(directory + "/extended.csv")

with open(filename, "r", newline="") as inputFile, open(
	newcsv, "w", newline="") as writerFile:

	reader = csv.DictReader(inputFile, delimiter=',')
	writer = csv.DictWriter(
		writerFile, fieldnames=["Wikidata ID", "Latitude", "Longitude"]
	)
	writer.writeheader()

	for row in reader:

		QID = row["Wikidata ID"]
		newrow = {"Wikidata ID": QID}

		try:
			entity = wbi.item.get(QID)
			lat = entity.claims.get("P625")[0].mainsnak.datavalue["value"]["latitude"]
			long = entity.claims.get("P625")[0].mainsnak.datavalue["value"]["longitude"]
			
			newrow = {"Wikidata ID": QID, "Latitude": lat, "Longitude": long}

		except:
			newrow = {"Wikidata ID": QID}

		writer.writerow(newrow)

inputFile.close()
writerFile.close()
