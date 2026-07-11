import os
import sys
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = r"E:\Internship\PocketFM\Next_Agency.xlsx"

def scrape_waterstones():
    print("Starting Waterstones Stealth Scraper (Cloudscraper Edition)...")
    
    df = pd.read_excel(EXCEL_FILE)
    
    base_url = "https://www.waterstones.com/category/romantic-fiction/fantasy-romance/sortmode/bestselling/page/"
    
    unique_books = set([str(t).strip().lower() for t in df['Name of Series'].dropna().tolist() if str(t).strip() != ''])
    new_rows = []
    
    page_num = max(1, (len(unique_books) // 24) + 1)
    
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    consecutive_empty = 0
    
    while len(unique_books) < 1300:
        url = f"{base_url}{page_num}"
        print(f"\n--- Scraping Page {page_num} ({url}) ---")
        
        try:
            response = scraper.get(url, timeout=30)
            if response.status_code != 200:
                print(f"Failed to fetch page! Status Code: {response.status_code}")
                time.sleep(5)
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            books = soup.select('.book-thumb, .book-preview')
            count = len(books)
            
            if count == 0:
                print("No books found! Reached the end or got blocked.")
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    print("3 consecutive empty pages. Ending.")
                    break
                page_num += 1
                time.sleep(2)
                continue
                
            consecutive_empty = 0
            added_this_page = 0
            
            for book in books:
                if len(unique_books) >= 1300:
                    break
                    
                title = ""
                img_tag = book.select_one('.image-wrap img')
                if img_tag and img_tag.has_attr('alt'):
                    title = img_tag['alt']
                    
                if not title:
                    title_tag = book.select_one('a.title, .title a')
                    if title_tag:
                        title = title_tag.get_text()
                        
                author = ""
                author_tag = book.select_one('.author a, .text-author')
                if author_tag:
                    author = author_tag.get_text()
                    
                title = title.strip()
                author = author.strip()
                
                if title and title.lower() not in unique_books:
                    safe_title = title.encode('ascii', 'ignore').decode('ascii')
                    safe_author = author.encode('ascii', 'ignore').decode('ascii')
                    print(f"  [{len(unique_books)+1}] Found: {safe_title} | {safe_author}")
                    
                    unique_books.add(title.lower())
                    added_this_page += 1
                    
                    row = {col: '' for col in df.columns}
                    row['Name of Series'] = title
                    row['Author Name'] = author
                    row['Publisher'] = 'Waterstones'
                    row['Name of agent in the main folder'] = 'Waterstones'
                    new_rows.append(row)
                    
            if added_this_page > 0:
                # Progressive Save
                pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True).to_excel(EXCEL_FILE, index=False)
            
            page_num += 1
            time.sleep(1) # Small delay to be polite
            
        except Exception as e:
            print(f"Error on page {page_num}: {e}")
            time.sleep(5)
            
    print(f"\nFinished. Successfully scraped {len(unique_books)} books.")
    apply_styling(EXCEL_FILE)
    print("Styling applied. ALL DONE!")

if __name__ == "__main__":
    scrape_waterstones()
