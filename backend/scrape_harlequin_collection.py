import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
df = pd.read_excel(excel_file)
existing_books = set(df['Name of Series'].dropna().astype(str))

base_url = 'https://harlequin.com/collections/harlequin-romance?meta.hc-product-mf.onSaleDateTimestamp=Current%20and%20previous%20months&sort=meta.hc-product-mf.onSaleDateTimestamp/DESC&page='
current_page = 1
total_new_books = 0

print("Starting Paginated Harlequin Collection Scraper...")

while True:
    url = f"{base_url}{current_page}"
    print(f"Scraping page {current_page}...")
    
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    # Check for blocking
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}. Stopping.")
        break
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = soup.find_all('div', class_='card-product')
    
    if not products:
        print("No products found on this page. Reached the end.")
        break
        
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
        # Safe incremental save
        df.to_excel(excel_file, index=False)
        for r in new_rows:
            existing_books.add(r['Name of Series'])
            
        total_new_books += len(new_rows)
        print(f"  -> Found {len(new_rows)} new unique books.")
    else:
        print("  -> No new unique books on this page.")
        
    # Check if there's a next button (optional failsafe, relying on empty products is safer)
    current_page += 1
    time.sleep(1) # Be nice to the server

print(f"\nScraping complete. Total new unique books scraped: {total_new_books}")
if total_new_books > 0:
    apply_styling(excel_file)
    print("Styling applied.")
