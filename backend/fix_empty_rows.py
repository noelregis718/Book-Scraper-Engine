import pandas as pd
import numpy as np
import sys

EXCEL_FILE = r"E:\Internship\PocketFM\books_from_uploaded_images.xlsx"
df = pd.read_excel(EXCEL_FILE)

# Fill NaNs with empty string for easy checking
df['Name of Series'] = df['Name of Series'].replace(np.nan, '')

# We want to drop rows where 'Name of Series' is empty
# BUT ONLY if it's one of the authors we know we just scraped books for (Liza Dawson authors)
# Or honestly, any row with an empty 'Name of Series' shouldn't be there because the top 5 books scraper
# appended the actual books further down!
initial_len = len(df)
df = df[df['Name of Series'].str.strip() != '']
final_len = len(df)

print(f"Dropped {initial_len - final_len} empty rows.")

df.to_excel(EXCEL_FILE, index=False)
print("Saved cleaned Excel file.")

try:
    sys.path.append(r"E:\Internship\PocketFM")
    import format_excel_script
    print("Formatting applied.")
except Exception as e:
    print(f"Formatting failed: {e}")
