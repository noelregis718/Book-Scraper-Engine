import pandas as pd
import os

file_path = r"E:\Internship\PocketFM\Crime_Thriller_Template.xlsx"
df = pd.read_excel(file_path)

columns_to_check = [
    'Goodreads Rating',
    'Goodreads No. of Ratings',
    'Series Link',
    'Part of Series',
    '# of primary books',
    'Book Number',
    'Goodreads Link'
]

print(f"Total Rows: {len(df)}")
print("-" * 30)

for col in columns_to_check:
    if col in df.columns:
        # Count NA values and empty strings
        empty_count = df[col].isna().sum() + (df[col] == "").sum() + (df[col].astype(str).str.strip() == "").sum() + (df[col] == "N/A").sum() + (df[col] == "nan").sum()
        print(f"{col}: {empty_count} missing out of {len(df)}")
    else:
        print(f"{col}: Column not found!")
