import pandas as pd
import os
import sys

base_dir = r"e:\Internship\PocketFM"
sys.path.append(os.path.join(base_dir, "backend"))

books_file = os.path.join(base_dir, "madeleine_milburn_books_scrape.xlsx")
authors_file = os.path.join(base_dir, "madeleine_milburn_authors.xlsx")
output_file = os.path.join(base_dir, "madeleine_milburn_combined.xlsx")

df_books = pd.read_excel(books_file)
df_authors = pd.read_excel(authors_file)

data_rows = []

# 1. Books
for idx, row in df_books.iterrows():
    title = str(row.get('Book Title', '')).strip()
    author = str(row.get('Author Name', '')).strip()
    if title.lower() == 'nan': title = ''
    if author.lower() == 'nan': author = ''
    
    data_rows.append({
        "Name of Series": title,
        "Author Name": author,
        "Publisher": "Madeleine Milburn Literary Agency",
        "GoodReads series link": "",
        "Number of PRIMARY books in the series": "",
        "Rating (out of 5) of Primary Book 1": "",
        "Ratings (#) of Primary Book 1": "",
        "Synopsis (if available)": "",
        "Romantasy = Yes or No?": "",
        "Romantasy Sub-Genre of series": "",
        "Name of agent": "Madeleine Milburn"
    })

# 2. Authors
for idx, row in df_authors.iterrows():
    author = str(row.get('Author Name', '')).strip()
    if not author or author.lower() == 'nan':
        continue
    data_rows.append({
        "Name of Series": "",
        "Author Name": author,
        "Publisher": "Madeleine Milburn Literary Agency",
        "GoodReads series link": "",
        "Number of PRIMARY books in the series": "",
        "Rating (out of 5) of Primary Book 1": "",
        "Ratings (#) of Primary Book 1": "",
        "Synopsis (if available)": "",
        "Romantasy = Yes or No?": "",
        "Romantasy Sub-Genre of series": "",
        "Name of agent": "Madeleine Milburn"
    })

df_combined = pd.DataFrame(data_rows)
df_combined.to_excel(output_file, index=False)

print(f"Combined sheet saved with {len(df_combined)} rows.")

from format_madwoman import format_madwoman
format_madwoman(output_file, output_file)

# Copy to downloads
os.system(r'powershell -Command "Copy-Item e:\Internship\PocketFM\madeleine_milburn_combined.xlsx -Destination C:\Users\noelr\Downloads\madeleine_milburn_combined.xlsx -Force"')
print("Formatting complete and copied to Downloads!")
