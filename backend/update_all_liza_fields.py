import pandas as pd
import sys
import os

EXCEL_FILE = r"E:\Internship\PocketFM\books_from_uploaded_images.xlsx"
df = pd.read_excel(EXCEL_FILE)

# Fill for all rows
df['Publisher'] = 'Liza Dawson Associates'
df['Name of agent'] = 'Liza Dawson'

df.to_excel(EXCEL_FILE, index=False)
print("Updated all rows with Publisher = 'Liza Dawson Associates' and Name of agent = 'Liza Dawson'.")

try:
    sys.path.append(r"E:\Internship\PocketFM\backend")
    from apply_jra_style import apply_styling
    apply_styling(EXCEL_FILE)
    print("Formatting applied.")
except Exception as e:
    print(f"Formatting failed: {e}")
