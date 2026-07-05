import pandas as pd
import sys
import os

sys.path.append('e:/Internship/PocketFM/backend')
from apply_jra_style import apply_styling

file_path = 'e:/Internship/PocketFM/Next_Agency.xlsx'
df = pd.read_excel(file_path)

changed = 0
def clean_author(x):
    global changed
    val = str(x).strip()
    if val.lower() in ['unknown', 'unknow', 'nan', '']:
        changed += 1
        return ''
    return x

df['Author Name'] = df['Author Name'].apply(clean_author)
df.to_excel(file_path, index=False)
apply_styling(file_path)

print(f'Successfully removed "Unknown" from {changed} rows.')
