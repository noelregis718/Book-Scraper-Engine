import pandas as pd
import json

df = pd.read_excel(r'E:\Internship\PocketFM\Knight Agency.xlsx')
data = df[['Name of Series', 'Author Name', 'Synopsis (if available)', 'Romantasy Sub-Genre of series']].to_dict(orient='records')

with open('scraped_books_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
