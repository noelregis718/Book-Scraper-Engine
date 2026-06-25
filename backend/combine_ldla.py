import pandas as pd
import os
import sys

columns = [
    "Name of Series",
    "Author Name",
    "Publisher",
    "GoodReads series link",
    "Number of PRIMARY books in the series",
    "Rating (out of 5) of Primary Book 1",
    "Ratings (#) of Primary Book 1",
    "Synopsis (if available)",
    "Romantasy = Yes or No?",
    "Romantasy Sub-Genre of series",
    "Name of agent in the main folder"
]

file1 = "e:/Internship/PocketFM/LDLA_Author_Books.xlsx"
file2 = "e:/Internship/PocketFM/LDLA_Books_and_Authors.xlsx"
file3 = "e:/Internship/PocketFM/Laura_Dail_Agency_Books.xlsx"

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)
df3 = pd.read_excel(file3)

df3 = df3.rename(columns={'Author': 'Author Name'})

combined = pd.concat([df1, df2, df3], ignore_index=True)
combined = combined.rename(columns={'Book Name': 'Name of Series'})

combined = combined.drop_duplicates(subset=['Name of Series', 'Author Name']).reset_index(drop=True)

for col in columns:
    if col not in combined.columns:
        combined[col] = ""

combined = combined[columns]

output_path = "e:/Internship/PocketFM/LDLA_Combined.xlsx"
combined.to_excel(output_path, index=False)
print(f"Created combined sheet at {output_path} with {len(combined)} rows.")

sys.path.append('e:/Internship/PocketFM/backend')
try:
    from apply_jra_style import apply_styling
    apply_styling(output_path)
    print("Applied standard styling.")
except Exception as e:
    print(f"Styling skipped or failed: {e}")
