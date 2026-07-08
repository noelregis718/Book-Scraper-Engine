import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

url = 'https://www.tell-talepublishing.com/store/c28/Paranormal%2FSupernatural.html'
excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")

def clean_title_author(raw_title):
    # Remove format tags like --PAPERBACK, -Digital Version, --DIGITAL, etc.
    title = re.sub(r'--?PAPERBACK.*$', '', raw_title, flags=re.IGNORECASE).strip()
    title = re.sub(r'--?DIGITAL.*$', '', title, flags=re.IGNORECASE).strip()
    title = re.sub(r'--?Digital Version.*$', '', title, flags=re.IGNORECASE).strip()
    
    author = ""
    # Look for ' by [Author]' in the title
    by_match = re.search(r'\s+by\s+(.*?)(?:, Book \d+)?$', title, flags=re.IGNORECASE)
    if by_match:
        author = by_match.group(1).strip()
        # Remove author from title
        title = title[:by_match.start()].strip()
        
    return title, author

async def run_scraper():
    print(f"Starting Playwright scraper for Tell-Tale Publishing...")
    
    df = pd.read_excel(excel_file)
    existing_books = set(df['Name of Series'].dropna().astype(str).str.lower().str.strip())
    new_rows = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        
        page_num = 1
        while True:
            print(f"Scraping Page {page_num}...")
            # Wait for products to load
            try:
                await page.wait_for_selector('.wsite-com-category-product-name', timeout=10000)
            except:
                print("No products found on this page or timeout reached.")
                break
                
            # Extract products
            elements = await page.query_selector_all('.wsite-com-category-product-name')
            titles = []
            for el in elements:
                t = await el.inner_text()
                titles.append(t.strip())
                
            print(f"Found {len(titles)} books on page {page_num}.")
            
            page_new_books = 0
            for raw_t in titles:
                title, author = clean_title_author(raw_t)
                
                if title and title.lower() not in existing_books:
                    row = {col: '' for col in df.columns}
                    row['Name of Series'] = title
                    row['Author Name'] = author
                    row['Publisher'] = 'Tell-Tale Publishing'
                    row['Name of agent in the main folder'] = 'Tell-Tale Publishing'
                    new_rows.append(row)
                    existing_books.add(title.lower())
                    page_new_books += 1
            
            # Save progressively
            if page_new_books > 0:
                df_temp = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                df_temp.to_excel(excel_file, index=False)
                
            if page_new_books == 0:
                print("No new books found on this page. Stopping to prevent infinite loop.")
                break
                    
            # Check for pagination Next button
            next_btn = await page.query_selector('a:has-text("Next")')
            if not next_btn:
                print("No 'Next' button found. Reached the end.")
                break
                
            # Click it
            print("Clicking 'Next'...")
            try:
                await next_btn.click()
                await page.wait_for_timeout(3000) # Wait for ajax load
                page_num += 1
            except Exception as e:
                print(f"Failed to click next: {e}")
                break
                
        await browser.close()
        
    print(f"Scraping finished. Found {len(new_rows)} new unique books.")
    
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df = pd.concat([df, df_new], ignore_index=True)
        df.to_excel(excel_file, index=False)
        try:
            apply_styling(excel_file)
            print("Applied styling successfully.")
        except Exception as e:
            print(f"Failed to apply style: {e}")
            
    print("ALL DONE!")

if __name__ == "__main__":
    asyncio.run(run_scraper())
