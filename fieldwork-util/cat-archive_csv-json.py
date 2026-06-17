import sys
sys.path.insert(0, '..')
import private
import private_paths as path
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename
import csv
import json

# current version as of 17 June 2026

# all praise be to Gemini...
# utility for creating JSON from old cataloging fields

# select working directory & set filenames
root = tk.Tk()
root.withdraw()
filename = askopenfilename(initialdir=path.default)
directory = os.path.split(filename)[0]

input_csv = filename
output_csv = os.path.join(directory + "/json.csv")
new_name = filename.removesuffix(".csv")  + "-json.csv"

print(output_csv)

def csv_to_hybrid_csv(input_csv_path, output_csv_path, multivalue_columns):
    with open(input_csv_path, mode="r", encoding="utf-8") as infile:
        csv_reader = csv.DictReader(infile)

        # Identify the first column header dynamically
        if csv_reader.fieldnames:
            recordID = csv_reader.fieldnames[0]
            galtags = csv_reader.fieldnames[32]
        else:
            raise ValueError("The input CSV file seems to have no headers.")

        # Prepare the new output CSV file
        # added gallery tags since a number seemingly were cleared out and i'd like to repurpose them and i'm running the feed anyway...
        output_headers = [recordID, galtags, "json"]

        with open(output_csv_path, mode="w", encoding="utf-8", newline="") as outfile:
            csv_writer = csv.DictWriter(outfile, fieldnames=output_headers)
            csv_writer.writeheader()

            for row in csv_reader:
                id = row[recordID]
                tag = row[galtags]

                # Process the pipe-separated fields for the remaining data
                for col in multivalue_columns:
                    if col in row:
                        if row[col]:
                            row[col] = [
                                item.strip() for item in row[col].split("|")
                            ]
                        else:
                            row[col] = []

                # Convert the remaining row dictionary into a single-line JSON string
                json_string = json.dumps(row)

                # Write the new CSV
                csv_writer.writerow(
                    {recordID: id, "json": json_string, galtags: tag}
                )

columns_to_split = ["Art Hum Unit", "Creator", "Culture", "Gallery Tags", "IDP Cultures", "Location", "Material/Technique", "MMM Gallery Tags", "Portfolio", "Repository", "Site", "Style/Period", "Subject", "Work Type"]

csv_to_hybrid_csv(input_csv, output_csv, columns_to_split)
os.rename(output_csv, new_name)
print('✧･ﾟ: *✧･ﾟ:* Done! *:･ﾟ✧*:･ﾟ✧\n')