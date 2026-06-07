import pandas as pd
import sys

EXCEL_FILE = r"E:\Internship\PocketFM\extracted_book_titles_authors.xlsx"
df = pd.read_excel(EXCEL_FILE)

# Identify rows where the author name contains "not legible" or "not eligible" or similar
# The original value was "Not legible in image"
count = 0
for idx, row in df.iterrows():
    author = str(row.get('Author Name', '')).strip().lower()
    if 'not legible' in author or 'not eligible' in author or author == 'nan':
        df.at[idx, 'Author Name'] = ""
        count += 1

df.to_excel(EXCEL_FILE, index=False)
print(f"Cleared 'Author Name' in {count} rows.")

try:
    sys.path.append(r"E:\Internship\PocketFM\backend")
    from apply_jra_style import apply_styling
    apply_styling(EXCEL_FILE)
    print("Formatting reapplied.")
except Exception as e:
    print(f"Formatting failed: {e}")
