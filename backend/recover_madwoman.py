import pandas as pd
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

raw_df = pd.read_excel(r'C:\Users\noelr\Downloads\madwoman_literary_scraped_books.xlsx')

rows = []
# 1. Add the 24 books
for idx, row in raw_df.iterrows():
    if pd.isna(row.get('Title')): continue
    rows.append({
        'Name of Series': row.get('Title', ''),
        'Author Name': row.get('Author', ''),
        'Publisher': '',
        'GoodReads series link': '',
        'Number of PRIMARY books in the series': '',
        'Rating (out of 5) of Primary Book 1': '',
        'Ratings (#) of Primary Book 1': '',
        'Synopsis (if available)': '',
        'Romantasy = Yes or No?': '',
        'Romantasy Sub-Genre of series': '',
        'Name of agent': 'Mad Woman Literary'
    })

# 2. Load the 97 authors from markdown
md_file = r"C:\Users\noelr\.gemini\antigravity-ide\brain\37f9affe-cb68-44e7-a2bf-9f63822bb435\.system_generated\steps\52\content.md"
authors = []
with open(md_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith("###### "):
            name = line.strip().replace("###### ", "")
            if "[" not in name and "]" not in name:
                authors.append(name)

# 3. Apply the Goodreads state for these authors
state_file = r'e:\Internship\PocketFM\backend\madwoman_state.json'
state = {}
if os.path.exists(state_file):
    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

for author in authors:
    if author in state:
        books = state[author]
        if not books:
            rows.append({
                'Name of Series': 'N/A',
                'Author Name': author,
                'Name of agent': 'Mad Woman Literary'
            })
        else:
            for b in books:
                rows.append({
                    'Name of Series': b.get('title', 'Unknown'),
                    'Author Name': author,
                    'GoodReads series link': b.get('GoodReads_Series_URL') or b.get('GoodReads_Book_URL', 'N/A'),
                    'Number of PRIMARY books in the series': b.get('Num_Primary_Books', 1),
                    'Rating (out of 5) of Primary Book 1': b.get('Book1_Rating', b.get('GoodReads_Rating', 'N/A')),
                    'Ratings (#) of Primary Book 1': b.get('Book1_Num_Ratings', b.get('GoodReads_Rating_Count', 'N/A')),
                    'Synopsis (if available)': b.get('Description', 'N/A'),
                    'Name of agent': 'Mad Woman Literary'
                })
    else:
        # Not yet scraped
        rows.append({
            'Name of Series': '',
            'Author Name': author,
            'Name of agent': 'Mad Woman Literary'
        })

df_new = pd.DataFrame(rows)
target_excel = r'e:\Internship\PocketFM\madwoman_literary_scraped_books.xlsx'
df_new.to_excel(target_excel, index=False)

from format_madwoman import format_madwoman
format_madwoman(target_excel, target_excel)
print(f"Recovery complete. {len(rows)} rows saved to {target_excel}")
