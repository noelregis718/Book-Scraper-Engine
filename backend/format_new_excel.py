import pandas as pd
import sys
import os

EXCEL_FILE = r"E:\Internship\PocketFM\extracted_book_titles_authors.xlsx"
df = pd.read_excel(EXCEL_FILE)

# Map the necessary columns
df = df.rename(columns={
    "Book title": "Name of Series",
    "Author (as visible)": "Author Name"
})

# Keep only the two required columns
df = df[["Name of Series", "Author Name"]]

# Add the remaining 9 columns
expected_columns = [
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
    "Name of agent"
]

for col in expected_columns:
    if col not in df.columns:
        df[col] = ""

# Reorder exactly
df = df[expected_columns]

# Save
df.to_excel(EXCEL_FILE, index=False)
print("Applied 11-column format successfully.")

try:
    sys.path.append(r"E:\Internship\PocketFM\backend")
    from apply_jra_style import apply_styling
    apply_styling(EXCEL_FILE)
    print("Formatting applied.")
except Exception as e:
    print(f"Formatting failed: {e}")
