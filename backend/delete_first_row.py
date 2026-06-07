import pandas as pd
import sys
import os

EXCEL_FILE = r"E:\Internship\PocketFM\books_from_uploaded_images.xlsx"
df = pd.read_excel(EXCEL_FILE)

# Print what we're deleting to be sure
first_row = df.iloc[0]
print(f"Deleting the first row of data: Author='{first_row.get('Author Name', '')}', Book='{first_row.get('Name of Series', '')}'")

# Drop the first row (index 0)
df = df.iloc[1:].reset_index(drop=True)

df.to_excel(EXCEL_FILE, index=False)
print("Deleted the first row and saved.")

try:
    sys.path.append(r"E:\Internship\PocketFM\backend")
    from apply_jra_style import apply_styling
    apply_styling(EXCEL_FILE)
    print("Formatting applied.")
except Exception as e:
    print(f"Formatting failed: {e}")
