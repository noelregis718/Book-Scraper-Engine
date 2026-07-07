import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys
import os
import concurrent.futures
from threading import Lock

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

base_url = 'https://www.bookstrand.com/books/erotic-romance'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
csv_file = os.path.join(os.path.dirname(__file__), "bookstrand_temp.csv")

csv_lock = Lock()
existing_titles = set()

def scrape_page(page_num):
    url = f"{base_url}?page={page_num}"
    try:
        # Increased timeout to handle slow trickle responses
        response = requests.get(url, headers=headers, timeout=(15, 30))
        if response.status_code != 200:
            return False, 0
            
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.find_all(class_='category-book')
        
        if not books:
            return False, 0
            
        new_rows = []
        for b in books:
            title_el = b.find(class_='category-book__title')
            title = title_el.text.strip() if title_el else ""
            
            author_el = b.find(class_='category-book__authors')
            author = author_el.find('a').text.strip() if author_el and author_el.find('a') else "Unknown"
            
            if title:
                title_lower = title.lower().strip()
                with csv_lock:
                    if title_lower not in existing_titles:
                        existing_titles.add(title_lower)
                        row = {
                            'Name of Series': title,
                            'Author Name': author,
                            'Publisher': 'Bookstrand',
                            'GoodReads series link': '',
                            'Number of PRIMARY books in the series': 1,
                            'Rating (out of 5) of Primary Book 1': 'N/A',
                            'Ratings (#) of Primary Book 1': 'N/A',
                            'Synopsis (if available)': 'N/A',
                            'Romantasy = Yes or No?': 'No',
                            'Romantasy Sub-Genre of series': '',
                            'Name of agent in the main folder': 'Bookstrand'
                        }
                        new_rows.append(row)
        
        if new_rows:
            df_new = pd.DataFrame(new_rows)
            with csv_lock:
                if not os.path.exists(csv_file):
                    df_new.to_csv(csv_file, index=False)
                else:
                    df_new.to_csv(csv_file, mode='a', header=False, index=False)
                    
        print(f"Page {page_num} finished. Found {len(new_rows)} new books.")
        return True, len(new_rows)
    except Exception as e:
        print(f"Error on page {page_num}: {e}")
        return False, 0

def main():
    global existing_titles
    df_excel = pd.read_excel(excel_file)
    existing_titles = set(df_excel['Name of Series'].dropna().astype(str).str.lower().str.strip())
    
    # Check if we have a CSV from a previous aborted run
    if os.path.exists(csv_file):
        df_csv = pd.read_csv(csv_file)
        existing_titles.update(set(df_csv['Name of Series'].dropna().astype(str).str.lower().str.strip()))
        print(f"Resuming with {len(df_csv)} books already in temp CSV...")
    
    total_added = 0
    max_pages = 601
    
    print(f"Scraping up to {max_pages} pages concurrently...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(scrape_page, p): p for p in range(1, max_pages + 1)}
        for future in concurrent.futures.as_completed(futures):
            p = futures[future]
            try:
                success, added = future.result()
                total_added += added
            except Exception as exc:
                print(f"Page {p} generated an exception: {exc}")
                
    print(f"Scraping finished. Transferring {total_added} books to Excel...")
    if os.path.exists(csv_file):
        df_csv = pd.read_csv(csv_file)
        # Ensure 11 columns
        for col in df_excel.columns:
            if col not in df_csv.columns:
                df_csv[col] = ''
        df_csv = df_csv[df_excel.columns]
        
        df_final = pd.concat([df_excel, df_csv], ignore_index=True)
        df_final.to_excel(excel_file, index=False)
        
        try:
            apply_styling(excel_file)
            print("Applied styling successfully.")
        except Exception as e:
            print(f"Failed to apply styling: {e}")
            
        os.remove(csv_file)
        
    print(f"\nALL DONE! Successfully compiled all books into the spreadsheet.")

if __name__ == '__main__':
    main()
