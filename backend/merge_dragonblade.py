import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from apply_jra_style import apply_styling
except ImportError:
    def apply_styling(p): pass

f1 = r'E:\Internship\PocketFM\Medieval_Romance_Books.xlsx'
f2 = r'E:\Internship\PocketFM\Regency_Romance_350_FINAL_50+.xlsx'
f3 = r'E:\Internship\PocketFM\dragonblade_georgian_romance_books_updated.xlsx'

df1 = pd.read_excel(f1)
df1 = df1.rename(columns={'Book Name': 'Name of Series'})

df2 = pd.read_excel(f2)
df2 = df2.rename(columns={'BOOK TITLE': 'Name of Series', 'AUTHOR': 'Author Name'})

df3 = pd.read_excel(f3)
df3 = df3.rename(columns={'Book Name': 'Name of Series'})

df1 = df1[['Name of Series', 'Author Name']].copy()
df2 = df2[['Name of Series', 'Author Name']].copy()
df3 = df3[['Name of Series', 'Author Name']].copy()

df1['Original Series / Category'] = 'Medieval Romance'
df2['Original Series / Category'] = 'Regency Romance'
df3['Original Series / Category'] = 'Georgian Romance'

combined = pd.concat([df1, df2, df3], ignore_index=True)

final_columns = [
    "Original Series / Category",
    "Name of Series",
    "Romantasy = Yes or No?",
    "Romantasy Sub-Genre of series",
    "Author Name",
    "Synopsis (if available)",
    "GoodReads series link",
    "GoodReads Average Rating",
    "GoodReads Total Ratings",
    "Publisher",
    "Name of agent"
]

for col in final_columns:
    if col not in combined.columns:
        combined[col] = ""

combined = combined[final_columns]
out_file = r'E:\Internship\PocketFM\dragonblade_books_combined.xlsx'
combined.to_excel(out_file, index=False)

try:
    apply_styling(out_file)
except Exception as e:
    print(f"Styling warning: {e}")

print(f"Merged successfully! Total rows: {len(combined)}")
