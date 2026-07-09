import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

BASE_URL = 'https://turnerpublishing.com'
START_URL = 'https://turnerpublishing.com/collections/middle-grade'
EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")

def scrape_turner():
    print(f"Starting extremely fast requests scraper for Turner Publishing...")
    
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
    existing_books = set(df['Name of Series'].dropna().astype(str).str.lower().str.strip())
    new_rows = []
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    current_url = START_URL
    page_num = 1
    
    while current_url:
        print(f"Scraping Page {page_num}...")
        try:
            response = session.get(current_url, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch {current_url}: {e}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract titles
        title_els = soup.find_all('h2', class_='productitem--title')
        titles = [t.text.strip() for t in title_els]
        
        print(f"Found {len(titles)} books on page {page_num}.")
        
        if not titles:
            print("No books found on this page. Reached the end.")
            break
            
        page_new = 0
        for title in titles:
            if title and title.lower() not in existing_books:
                row = {col: '' for col in df.columns}
                row['Name of Series'] = title
                row['Author Name'] = ''  # User explicitly requested to scrape name only and leave author blank
                row['Publisher'] = 'Turner Publishing'
                row['Name of agent in the main folder'] = 'Turner Publishing'
                new_rows.append(row)
                existing_books.add(title.lower())
                page_new += 1
                
        # Progressive save
        if page_new > 0:
            df_temp = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            df_temp.to_excel(EXCEL_FILE, index=False)
            
        # Check for next page
        next_btn = soup.find('li', class_='pagination--next')
        if next_btn:
            a_tag = next_btn.find('a')
            if a_tag and a_tag.get('href'):
                current_url = BASE_URL + a_tag['href']
                page_num += 1
                continue
                
        print("No 'Next' button found. Scraping complete.")
        break
        
    print(f"Finished. Found {len(new_rows)} new unique books.")
    
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df = pd.concat([df, df_new], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        try:
            apply_styling(EXCEL_FILE)
            print("Applied styling successfully.")
        except Exception as e:
            print(f"Failed to apply style: {e}")
            
    print("ALL DONE!")

if __name__ == "__main__":
    scrape_turner()
