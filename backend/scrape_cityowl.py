import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Next_Agency.xlsx')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def run():
    print("Starting City Owl Press scraper (Maintaining Page Order)...")
    all_books = [] # Use list to maintain order instead of set
    seen = set()
    page = 1
    
    while True:
        url = f"https://cityowlpress.com/collections/all?page={page}"
        print(f"Scraping page {page}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch page {page}: {e}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titles_on_page = 0
        for title_elem in soup.find_all(class_='card__heading'):
            title = title_elem.text.strip()
            if title:
                if title not in seen:
                    seen.add(title)
                    all_books.append(title)
                    titles_on_page += 1
                    
        print(f"Found {titles_on_page} unique new books on page {page}.")
        
        if titles_on_page == 0:
            print("No more books found. Finishing scrape.")
            break
            
        page += 1
        time.sleep(1)
        
    print(f"\nTotal unique books scraped: {len(all_books)}")
    
    # Overwrite the Excel sheet so we can have them in pure page order
    columns = [
        'Name of Series', 'Author Name', 'Publisher', 'GoodReads series link', 
        'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1', 
        'Ratings (#) of Primary Book 1', 'Synopsis (if available)', 
        'Romantasy = Yes or No?', 'Romantasy Sub-Genre of series', 
        'Name of agent in the main folder'
    ]
    df = pd.DataFrame(columns=columns)
        
    new_rows = []
    for book in all_books: # Do not sort here!
        new_row = {col: '' for col in df.columns}
        new_row['Name of Series'] = book
        new_row['Publisher'] = 'City Owl Press'
        new_rows.append(new_row)
        
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        print("Successfully saved to Next_Agency.xlsx")
        
        try:
            apply_styling(EXCEL_FILE)
            print("Styling applied.")
        except:
            pass

if __name__ == '__main__':
    run()
