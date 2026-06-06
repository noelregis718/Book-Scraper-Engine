import pandas as pd
import sys
import subprocess
import os

cols = [
    'Name of Series', 
    'Author Name', 
    'Publisher', 
    'GoodReads series link', 
    'Number of PRIMARY books in the series', 
    'Rating (out of 5) of Primary Book 1', 
    'Ratings (#) of Primary Book 1', 
    'Synopsis (if available)', 
    'Romantasy = Yes or No?', 
    'Romantasy Sub-Genre of series', 
    'Name of agent'
]

df = pd.DataFrame(columns=cols)
EXCEL_FILE = r'E:\Internship\PocketFM\rebecca_freidmann_authors.xlsx'
df.to_excel(EXCEL_FILE, index=False)

sys.path.append(r'E:\Internship\PocketFM\backend')
try:
    from apply_jra_style import apply_styling
    apply_styling(EXCEL_FILE)
except Exception as e:
    print('Styling failed:', e)

subprocess.Popen(['start', EXCEL_FILE], shell=True)
print('Created new empty Excel sheet successfully!')
