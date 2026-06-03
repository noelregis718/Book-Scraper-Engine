import pandas as pd
import sys
import os

sys.path.append(r'E:\Internship\PocketFM\backend')
try:
    from apply_jra_style import apply_styling
except ImportError:
    def apply_styling(p): pass

f = r'E:\Internship\PocketFM\dragonblade_books_combined.xlsx'
df = pd.read_excel(f)

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

for c in cols:
    if c not in df.columns:
        df[c] = ''

df = df[cols]
df.to_excel(f, index=False)
apply_styling(f)
print('Done formatting columns.')
