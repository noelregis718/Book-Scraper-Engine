import pandas as pd
import os
import sys

sys.path.append(r'e:\Internship\PocketFM\backend')
from format_madwoman import format_madwoman

EXCEL_FILE = r'e:\Internship\PocketFM\madeleine_milburn_combined.xlsx'

df = pd.read_excel(EXCEL_FILE)

df.at[633, 'Romantasy = Yes or No?'] = 'Yes'
df.at[633, 'Romantasy Sub-Genre of series'] = 'Cozy / Cottagecore'

df.at[634, 'Romantasy = Yes or No?'] = 'Yes'
df.at[634, 'Romantasy Sub-Genre of series'] = 'Cozy / Cottagecore'

df.to_excel(EXCEL_FILE, index=False)
format_madwoman(EXCEL_FILE, EXCEL_FILE)

os.system(r'powershell -Command "Copy-Item e:\Internship\PocketFM\madeleine_milburn_combined.xlsx -Destination C:\Users\noelr\Downloads\madeleine_milburn_combined.xlsx -Force"')

print("Success!")
