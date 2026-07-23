import pandas as pd

file_path = r"e:\Internship\PocketFM\All-Genre Licensing Tracker.xlsx"
sheet_name = "Romantasy v2"

print("Reading excel file...")
df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

# The actual headers are in Excel Row 2 (index 1). We'll also keep Row 1 (index 0) just in case it has notes.
header_rows = df.iloc[0:2] # Excel rows 1 and 2

rows_1 = df.iloc[146:190] # Excel rows 147 to 190
rows_2 = df.iloc[194:233] # Excel rows 195 to 233

# Combine them
result_df = pd.concat([header_rows, rows_1, rows_2])

output_file = r"e:\Internship\PocketFM\Romantasy_v2_extracted.xlsx"
result_df.to_excel(output_file, index=False, header=False)
print(f"Extraction complete with headers. Saved to {output_file}")
