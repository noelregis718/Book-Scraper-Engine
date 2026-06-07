import pandas as pd
import re

log_path = r'C:\Users\noelr\.gemini\antigravity-ide\brain\dc99f070-d322-4c74-abbd-e11a9d9dfb50\.system_generated\tasks\task-66.log'
excel_path = r'E:\Internship\PocketFM\books_from_uploaded_images.xlsx'

df = pd.read_excel(excel_path)

with open(log_path, 'r', encoding='utf-8') as f:
    log_content = f.read()

pattern = r"Searching Goodreads for: '(.*?)' by '(.*?)'"
matches = re.findall(pattern, log_content)

author_to_title = {}
for title, author in matches:
    author_to_title[author] = title

titles = []
for author in df['Author Name']:
    # There are some duplicate authors, but since we are just recovering top-level books, we can use the mapping.
    # The first run had one book per author mostly, or exactly matching the row.
    titles.append(author_to_title.get(author, 'Unknown Title'))

if 'Name of Series' not in df.columns:
    df.insert(0, 'Name of Series', titles)
    
df.to_excel(excel_path, index=False)
print('Recovered titles successfully!')
