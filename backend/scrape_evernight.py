import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
import time
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Next_Agency.xlsx')

def run():
    print("Starting Evernight Publishing Scraper...")
    
    # Load existing to append properly
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        existing_books = set(df['Name of Series'].dropna().str.strip())
    else:
        columns = [
            'Name of Series', 'Author Name', 'Publisher', 'GoodReads series link', 
            'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1', 
            'Ratings (#) of Primary Book 1', 'Synopsis (if available)', 
            'Romantasy = Yes or No?', 'Romantasy Sub-Genre of series', 
            'Name of agent in the main folder'
        ]
        df = pd.DataFrame(columns=columns)
        existing_books = set()

    all_new_rows = []
    page = 1
    
    while True:
        url = f"https://www.evernightpublishing.com/mc-romance/?page={page}"
        print(f"Scraping page {page}...")
        
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch page {page}: {e}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Evernight titles contain the author: "Book Title by Author Name"
        items = soup.select('.product-item-title a')
        
        if not items:
            print("No more books found. Reached end of pagination.")
            break
            
        books_on_page = 0
        for item in items:
            raw_text = item.text.strip()
            
            # Split by the LAST occurrence of " by " to handle titles that contain "by"
            parts = raw_text.rsplit(" by ", 1)
            title = parts[0].strip()
            author = parts[1].strip() if len(parts) > 1 else ""
            
            # Additional cleanup if needed (e.g., removing leading quotes)
            title = re.sub(r'^["\']|["\']$', '', title)
            
            if title and title not in existing_books and not any(r['Name of Series'] == title for r in all_new_rows):
                new_row = {col: '' for col in df.columns}
                new_row['Name of Series'] = title
                new_row['Author Name'] = author
                new_row['Publisher'] = 'Evernight Publishing'
                all_new_rows.append(new_row)
                books_on_page += 1
                
        print(f"Found {books_on_page} unique new books on page {page}.")
        
        # BigCommerce usually returns identical items on out-of-bound pages, or empty
        if books_on_page == 0:
            print("No new books found. Reached end of pagination.")
            break
            
        page += 1
        time.sleep(1.5)
        
    print(f"\nTotal new unique books scraped: {len(all_new_rows)}")
    
    if all_new_rows:
        df = pd.concat([df, pd.DataFrame(all_new_rows)], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        print("Successfully appended to Next_Agency.xlsx")
        
        try:
            apply_styling(EXCEL_FILE)
            print("Styling applied.")
        except Exception as e:
            print(f"Styling error: {e}")
    else:
        print("No new books to append.")

if __name__ == '__main__':
    run()
