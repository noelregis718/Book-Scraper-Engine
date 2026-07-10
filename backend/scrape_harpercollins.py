import os
import sys
import pandas as pd
import requests
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

BASE_URL = 'https://harpercollins.co.uk/collections/romance/products.json?limit=250&page={}'
EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")

def scrape_harpercollins_api():
    print("Starting ultra-fast API scraper for HarperCollins UK (Romance)...")
    
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
    existing_books = set(df['Name of Series'].dropna().astype(str).str.lower().str.strip())
    new_rows = []
    
    books_scraped = 0
    target_books = 200
    page = 1
    
    while books_scraped < target_books:
        print(f"Fetching page {page}...")
        try:
            url = BASE_URL.format(page)
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            data = response.json()
            products = data.get('products', [])
            if not products:
                print("No more products found.")
                break
                
            print(f"Successfully fetched {len(products)} products from HarperCollins API!")
            
            for p in products:
                if books_scraped >= target_books:
                    break
                    
                title = p.get('title', '').strip()
                if not title: continue
                
                # Extract author from image alt text
                author = ""
                images = p.get('images', [])
                if images:
                    alt = images[0].get('alt')
                    if alt:
                        m = re.search(r' by (.*?)(?: \(|$)', alt)
                        if m: author = m.group(1).strip()
                        
                if title and title.lower() not in existing_books:
                    print(f"Found [{books_scraped+1}/{target_books}]: {title} | Author: {author}")
                    row = {col: '' for col in df.columns}
                    row['Name of Series'] = title
                    row['Author Name'] = author
                    row['Publisher'] = 'HarperCollins UK'
                    row['Name of agent in the main folder'] = 'HarperCollins UK'
                    new_rows.append(row)
                    existing_books.add(title.lower())
                    books_scraped += 1
            
            page += 1
            
        except Exception as e:
            print(f"Failed to fetch API data: {e}")
            break
            
    print(f"\nFinished. Found {len(new_rows)} new unique books.")
    
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df_final = pd.concat([df, df_new], ignore_index=True)
        df_final.to_excel(EXCEL_FILE, index=False)
        try:
            apply_styling(EXCEL_FILE)
            print("Applied styling successfully.")
        except Exception as e:
            print(f"Failed to apply style: {e}")
            
    print("ALL DONE!")

if __name__ == "__main__":
    scrape_harpercollins_api()
