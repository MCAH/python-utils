import csv
import json

# all praise be to Gemini...

def csv_to_hybrid_csv(input_csv_path, output_csv_path, multivalue_columns):
    with open(input_csv_path, mode="r", encoding="utf-8") as infile:
        csv_reader = csv.DictReader(infile)

        # Identify the first column header dynamically
        if csv_reader.fieldnames:
            first_column = csv_reader.fieldnames[0]
        else:
            raise ValueError("The input CSV file seems to have no headers.")

        # Prepare the new output CSV file with two columns:
        # 1. The original first column name
        # 2. A new column named 'json_data'
        output_headers = [first_column, "json_data"]

        with open(output_csv_path, mode="w", encoding="utf-8", newline="") as outfile:
            csv_writer = csv.DictWriter(outfile, fieldnames=output_headers)
            csv_writer.writeheader()

            for row in csv_reader:
                # 1. Extract and save the first column's value
                first_column_value = row[first_column]

                # 3. Process the pipe-separated fields for the remaining data
                for col in multivalue_columns:
                    if col in row:
                        if row[col]:
                            row[col] = [
                                item.strip() for item in row[col].split("|")
                            ]
                        else:
                            row[col] = []

                # 4. Convert the remaining row dictionary into a single-line JSON string
                json_string = json.dumps(row)

                # 5. Write the 2-column row to the new CSV
                csv_writer.writerow(
                    {first_column: first_column_value, "json_data": json_string}
                )


# --- Usage ---
input_csv = "my_data.input.csv"
output_csv = "my_data.output.csv"

# Update this list with your pipe-separated columns
columns_to_split = ["Location", "Culture"]

csv_to_hybrid_csv(input_csv, output_csv, columns_to_split)
print(f"Successfully created hybrid CSV at '{output_csv}'!")