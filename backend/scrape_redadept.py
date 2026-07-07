import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

url = 'https://redadeptpublishing.com/womensfiction/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
}

print(f"Fetching {url}...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

products = soup.find_all('li', class_='product')
print(f"Found {len(products)} romance books.")

excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
df = pd.read_excel(excel_file)
existing_books = set(df['Name of Series'].dropna().astype(str))

# Categories that are NOT author names
IGNORE_CATS = {
    'product_cat-romance', 'product_cat-womens-fiction', 'product_cat-historical-fiction',
    'product_cat-contemporary-romance', 'product_cat-paranormal-romance', 'product_cat-romantic-suspense',
    'product_cat-erotica', 'product_cat-new-adult', 'product_cat-young-adult', 'product_cat-fantasy',
    'product_cat-science-fiction', 'product_cat-mystery', 'product_cat-thriller', 'product_cat-horror',
    'product_cat-suspense', 'product_cat-urban-fantasy', 'product_cat-epic-fantasy', 'product_cat-nonfiction',
    'product_cat-humor', 'product_cat-chick-lit', 'product_cat-literary-fiction', 'product_cat-action-adventure'
}

new_rows = []
for p in products:
    title_el = p.find('h2', class_='woocommerce-loop-product__title')
    title = title_el.text.strip() if title_el else ""
    
    # Try to extract author from product_cat-[author-slug] classes
    author = ""
    classes = p.get('class', [])
    for c in classes:
        if c.startswith('product_cat-') and c not in IGNORE_CATS:
            slug = c.replace('product_cat-', '')
            # Convert slug to name (e.g. fern-ronay -> Fern Ronay)
            author = " ".join([word.capitalize() for word in slug.split('-')])
            break
            
    if title and title not in existing_books and not any(r['Name of Series'] == title for r in new_rows):
        new_row = {col: '' for col in df.columns}
        new_row['Name of Series'] = title
        new_row['Author Name'] = author
        new_row['Publisher'] = 'Red Adept Publishing'
        new_row['Name of agent in the main folder'] = 'Red Adept Publishing' # Defaulting agent to publisher for now
        new_rows.append(new_row)

if new_rows:
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    df.to_excel(excel_file, index=False)
    apply_styling(excel_file)
    print(f"Successfully appended {len(new_rows)} new books to {excel_file}.")
else:
    print("No new unique books found to append.")
