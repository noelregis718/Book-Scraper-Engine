import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

import builtins
print = lambda *args, **kwargs: builtins.print(*args, **{**kwargs, 'flush': True})
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
file_lock = asyncio.Lock()

async def safe_save(df):
    async with file_lock:
        try:
            df.to_excel(EXCEL_FILE, index=False)
        except Exception as e:
            print(f"Error saving excel: {e}", flush=True)

async def scrape_panmacmillan():
    print(f"Loading Excel file: {EXCEL_FILE}", flush=True)
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
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        page = await context.new_page()
        
        start_url = "https://www.panmacmillan.com.au/book-shop/?category%5B%5D=624"
        print(f"Navigating to {start_url}")
        
        await page.goto(start_url, wait_until="domcontentloaded")
        await asyncio.sleep(4) # Wait for Cloudflare/JS
        
        current_page = 1
        
        while True:
            print(f"\nScraping page {current_page}...")
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
                tag.decompose()
            
            text = soup.get_text(separator='\n')
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            books_found = 0
            for i, line in enumerate(lines):
                if line == "BUY":
                    if i >= 2:
                        author = lines[i-1]
                        title = lines[i-2]
                        if title.startswith("Show "):
                            continue
                        
                        # Clean up author if needed
                        if author.lower().startswith('by '):
                            author = author[3:].strip()
                        if author.lower().startswith('by:'):
                            author = author[3:].strip()
                            
                        if title and title not in existing_books and not any(r['Name of Series'] == title for r in all_new_rows):
                            new_row = {col: '' for col in df.columns}
                            new_row['Name of Series'] = title
                            new_row['Author Name'] = author
                            new_row['Publisher'] = 'Pan Macmillan'
                            all_new_rows.append(new_row)
                            books_found += 1
            print(f"Found {books_found} unique new books on page {current_page}.")
            
            if books_found == 0:
                print("No new books found. Reached the end of pagination loop.")
                break
            
            # Try to click the "Next" button for WordPress Pagination
            next_btn = await page.query_selector('a.next.page-numbers')
            if next_btn:
                print("Navigating to next page...")
                current_page += 1
                await next_btn.click(force=True)
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(4)
            else:
                # No next button found, we reached the end
                print("No 'Next' page button found. Reached the end of the catalogue.")
                break
                
            # Incremental save
            if all_new_rows:
                temp_df = pd.concat([df, pd.DataFrame(all_new_rows)], ignore_index=True)
                await safe_save(temp_df)
                
        await browser.close()
        
    print(f"\nTotal new unique books scraped: {len(all_new_rows)}")
    
    if all_new_rows:
        df = pd.concat([df, pd.DataFrame(all_new_rows)], ignore_index=True)
        await safe_save(df)
        print("Successfully appended to Next_Agency.xlsx")
        
        try:
            apply_styling(EXCEL_FILE)
            print("Styling applied.")
        except Exception as e:
            print(f"Styling error: {e}")
    else:
        print("No new books to append.")

if __name__ == '__main__':
    asyncio.run(scrape_panmacmillan())
