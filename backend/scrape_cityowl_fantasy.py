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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def run():
    print("Starting City Owl Press (Fantasy Romance) scraper to APPEND...")
    
    # Read existing sheet so we can append exactly after the existing books
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        columns = [
            'Name of Series', 'Author Name', 'Publisher', 'GoodReads series link', 
            'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1', 
            'Ratings (#) of Primary Book 1', 'Synopsis (if available)', 
            'Romantasy = Yes or No?', 'Romantasy Sub-Genre of series', 
            'Name of agent in the main folder'
        ]
        df = pd.DataFrame(columns=columns)

    all_books = []
    seen = set()
    page = 1
    
    while True:
        url = f"https://cityowlpress.com/collections/fantasy-romance/fantasy-romance?page={page}"
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
                    all_books.append(title) # Do not deduplicate against Excel, append exactly as user requested!
                    titles_on_page += 1
                    
        print(f"Found {titles_on_page} unique books on page {page}.")
        
        items_on_page = len(soup.find_all(class_='card__heading'))
        if items_on_page == 0:
            print("No more books found on website. Finishing scrape.")
            break
            
        page += 1
        time.sleep(1)
        
    print(f"\nTotal fantasy romance books scraped to append: {len(all_books)}")
    
    new_rows = []
    for book in all_books:
        new_row = {col: '' for col in df.columns}
        new_row['Name of Series'] = book
        new_row['Publisher'] = 'City Owl Press'
        new_rows.append(new_row)
        
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Successfully appended {len(new_rows)} rows to Next_Agency.xlsx")
        
        try:
            apply_styling(EXCEL_FILE)
            print("Styling applied.")
        except:
            pass
    else:
        print("No new books to save.")

if __name__ == '__main__':
    run()
