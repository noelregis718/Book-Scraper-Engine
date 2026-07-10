import os
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

BASE_URL = 'https://www.austinmacauley.com/genre/contemporary-fiction?page={}'
EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")

def scrape_austin():
    print("Starting requests scraper for Austin Macauley...")
    
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
    existing_books = set(df['Name of Series'].dropna().astype(str).str.lower().str.strip())
    new_rows = []
    
    page = 1
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    while True:
        print(f"Scraping Page {page}...")
        url = BASE_URL.format(page)
        
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
        soup = BeautifulSoup(r.text, 'html.parser')
        articles = soup.find_all('article', class_=re.compile(r'product', re.I))
        
        if not articles:
            print("No more books found.")
            break
            
        page_new = 0
        for a in articles:
            title_el = a.find(['h5', 'h3', 'h4'])
            if not title_el: continue
            title = title_el.text.strip()
            
            author_div = a.find('div', class_='font-size-2 mb-2 text-truncate')
            author = ""
            if author_div:
                author = author_div.text.strip()
                
            if title and title.lower() not in existing_books:
                safe_title = title.encode('ascii', 'ignore').decode('ascii')
                safe_author = author.encode('ascii', 'ignore').decode('ascii')
                print(f"  Found: {safe_title} | Author: {safe_author}")
                row = {col: '' for col in df.columns}
                row['Name of Series'] = title
                row['Author Name'] = author
                row['Publisher'] = 'Austin Macauley'
                row['Name of agent in the main folder'] = 'Austin Macauley'
                new_rows.append(row)
                existing_books.add(title.lower())
                page_new += 1
                
        # Progressive save
        if page_new > 0:
            pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True).to_excel(EXCEL_FILE, index=False)
            
        # Look for next page
        next_btn = soup.find('a', {'rel': 'next'})
        if not next_btn and "href=\"?page=" + str(page + 1) + "\"" not in r.text and "href=\"https://www.austinmacauley.com/genre/erotica-romance-fiction?page=" + str(page + 1) + "\"" not in r.text:
            print("No 'Next' button found. Scraping complete.")
            break
            
        page += 1

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
    scrape_austin()
