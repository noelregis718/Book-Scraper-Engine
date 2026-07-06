import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

url = 'https://harlequin.com/pages/romance-bestsellers'
print(f"Fetching {url}...")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.text, 'html.parser')

products = soup.find_all('div', class_='card-product')
print(f"Found {len(products)} romance bestsellers.")

excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
df = pd.read_excel(excel_file)
existing_books = set(df['Name of Series'].dropna().astype(str))

new_rows = []
for p in products:
    title_el = p.find('h3', class_='card-product__title')
    title = title_el.text.strip() if title_el else ""
    
    author_el = p.find('p', class_='card-product__detail')
    author = ""
    if author_el and author_el.find('a'):
        author = author_el.find('a').text.strip()
        
    if title and title not in existing_books and not any(r['Name of Series'] == title for r in new_rows):
        new_row = {col: '' for col in df.columns}
        new_row['Name of Series'] = title
        new_row['Author Name'] = author
        new_row['Publisher'] = 'Harlequin'
        new_rows.append(new_row)

if new_rows:
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    df.to_excel(excel_file, index=False)
    apply_styling(excel_file)
    print(f"Successfully appended {len(new_rows)} new books to {excel_file}.")
else:
    print("No new unique books found to append.")
