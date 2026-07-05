import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Next_Agency.xlsx')

async def run():
    print("Starting Deep Desires Press scraper (Maintaining Page Order)...")
    all_books = [] 
    seen = set()
    
    async with async_playwright() as p:
        # Launch visible browser for the user
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.deepdesirespress.com/mf-straight/", wait_until="networkidle")
        
        page_num = 1
        while True:
            print(f"Scraping page {page_num}...")
            # Give page time to ensure elements are there
            await page.wait_for_timeout(3000)
            
            # Extract titles regardless of 'visibility' state
            titles = await page.locator(".pt-cv-title").all_inner_texts()
            
            titles_on_page = 0
            for raw_title in titles:
                title = raw_title.strip()
                if title and title not in seen:
                    seen.add(title)
                    all_books.append(title)
                    titles_on_page += 1
                    
            print(f"Found {titles_on_page} unique new books on page {page_num}.")
            
            # Look for the 'Next' button (class contains 'next' or text is '')
            next_btn = page.locator(".pt-cv-pagination a", has_text="»")
            
            if await next_btn.count() > 0:
                print("Clicking to next page...")
                await next_btn.first.click(force=True)
                # Wait for the AJAX content to change
                await page.wait_for_timeout(4000)
                page_num += 1
            else:
                print("No more pages found. Finishing scrape.")
                break
                
        await browser.close()
        
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
    for book in all_books:
        new_row = {col: '' for col in df.columns}
        new_row['Name of Series'] = book
        new_row['Publisher'] = 'Deep Desires Press'
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
    asyncio.run(run())
