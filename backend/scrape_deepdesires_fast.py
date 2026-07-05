import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Next_Agency.xlsx')

def run():
    print("Starting Fast Deep Desires Press Scraper...")
    
    # Load existing to avoid duplicates
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

    all_new_books = []
    page = 1
    
    while True:
        url = f"https://deepheartsya.com/books/?_page={page}"
        print(f"Scraping page {page}...")
        
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch page {page}: {e}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        titles = [t.text.strip() for t in soup.find_all(class_='pt-cv-title')]
        
        if not titles:
            print("No more books found. Finishing scrape.")
            break
            
        titles_on_page = 0
        for title in titles:
            if title and title not in existing_books and title not in all_new_books:
                all_new_books.append(title)
                titles_on_page += 1
                
        print(f"Found {titles_on_page} unique new books on page {page}.")
        
        if titles_on_page == 0:
            print("No new books found. Reached end of pagination. Finishing scrape.")
            break
            
        page += 1
        time.sleep(1)
        
    print(f"\nTotal new unique books scraped: {len(all_new_books)}")
    
    if all_new_books:
        new_rows = []
        for book in all_new_books:
            new_row = {col: '' for col in df.columns}
            new_row['Name of Series'] = book
            new_row['Publisher'] = 'Deep Hearts YA'
            new_rows.append(new_row)
            
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
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
