import pandas as pd
import sys

EXCEL_FILE = r"E:\Internship\PocketFM\books_from_uploaded_images.xlsx"
df = pd.read_excel(EXCEL_FILE)

# Identify rows for the recently added Liza Dawson authors
mask = df['Name of agent'] == 'Liza Dawson Associates'

# Update fields
df.loc[mask, 'Publisher'] = 'Liza Dawson Associates'
df.loc[mask, 'Name of agent'] = 'Liza Dawson'

df.to_excel(EXCEL_FILE, index=False)
print(f"Updated {mask.sum()} rows with Publisher = 'Liza Dawson Associates' and Name of agent = 'Liza Dawson'.")

try:
    sys.path.append(r"E:\Internship\PocketFM")
    import format_excel_script
    print("Formatting applied.")
except Exception as e:
    print(f"Formatting failed: {e}")
