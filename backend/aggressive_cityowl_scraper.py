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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def scrape_url(base_url):
    print(f"\n--- Aggressively Scraping: {base_url} ---")
    
    # Read existing sheet
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
        url = f"{base_url}?page={page}" if '?' not in base_url else f"{base_url}&page={page}"
        print(f"-> Fetching page {page}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch page {page}: {e}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titles_on_page = 0
        # Fast extraction
        for title_elem in soup.find_all(class_='card__heading'):
            title = title_elem.text.strip()
            if title:
                if title not in seen:
                    seen.add(title)
                    all_books.append(title)
                    titles_on_page += 1
                    
        print(f"   Found {titles_on_page} books on page {page}.")
        
        # Stop condition
        if len(soup.find_all(class_='card__heading')) == 0:
            print("   [!] No more books found. Moving to save.")
            break
            
        page += 1
        time.sleep(0.2) # Aggressive but safe enough
        
    print(f"Finished scraping {base_url}. Total books found: {len(all_books)}")
    
    if not all_books:
        return
        
    new_rows = []
    for book in all_books:
        new_row = {col: '' for col in df.columns}
        new_row['Name of Series'] = book
        new_row['Publisher'] = 'City Owl Press'
        new_rows.append(new_row)
        
    # Append strictly to the end
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    print(f"Successfully appended {len(new_rows)} rows to Next_Agency.xlsx")
    
    try:
        apply_styling(EXCEL_FILE)
        print("Styling applied.")
    except:
        pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python aggressive_cityowl_scraper.py <url1> <url2> ...")
        sys.exit(1)
        
    urls = sys.argv[1:]
    for url in urls:
        scrape_url(url)
