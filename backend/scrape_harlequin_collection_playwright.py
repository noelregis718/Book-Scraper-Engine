import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
df = pd.read_excel(excel_file)
existing_books = set(df['Name of Series'].dropna().astype(str))

base_url = 'https://harlequin.com/collections/harlequin-romance?meta.hc-product-mf.onSaleDateTimestamp=Current%20and%20previous%20months&sort=meta.hc-product-mf.onSaleDateTimestamp/DESC&page='
current_page = 1
total_new_books = 0
all_new_rows = []

async def run():
    global current_page, total_new_books, df, all_new_rows
    print("Starting Paginated Harlequin Playwright Scraper (Click-based)...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        page = await context.new_page()
        
        url = 'https://harlequin.com/collections/harlequin-romance?meta.hc-product-mf.onSaleDateTimestamp=Current%20and%20previous%20months&sort=meta.hc-product-mf.onSaleDateTimestamp/DESC&page=1'
        print(f"\nNavigating to initial page...")
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
        except Exception:
            print("Network idle timeout, proceeding to parse...")
            
        print("Waiting 15 seconds for you to bypass any security...")
        await asyncio.sleep(15)
        
        while True:
            print(f"\nScraping page {current_page}...")
                
            # Scroll to trigger lazy loading of Algolia items
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Use the foolproof text extraction method
            for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "template"]):
                tag.decompose()
                
            text = soup.get_text(separator='\n')
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            books_found = 0
            page_new_rows = []
            
            for i, line in enumerate(lines):
                if line.startswith("On Sale Date:"):
                    if i >= 2:
                        author = lines[i-1]
                        title = lines[i-2]
                        
                        # Exclude artifacts
                        if title == "List" or title == "Grid" or title == "View:" or title.startswith("Price:"):
                            continue
                            
                        if title and title not in existing_books and not any(r['Name of Series'] == title for r in all_new_rows):
                            new_row = {col: '' for col in df.columns}
                            new_row['Name of Series'] = title
                            new_row['Author Name'] = author
                            new_row['Publisher'] = 'Harlequin'
                            page_new_rows.append(new_row)
                            all_new_rows.append(new_row)
                            books_found += 1
                            
            print(f"Found {books_found} unique new books on page {current_page}.")
            
            if books_found == 0:
                print("No new books found. Stopping.")
                break
                
            # Save incrementally
            df = pd.concat([df, pd.DataFrame(page_new_rows)], ignore_index=True)
            df.to_excel(excel_file, index=False)
            for r in page_new_rows:
                existing_books.add(r['Name of Series'])
                
            total_new_books += books_found
            
            # Try to click next page
            next_btn = await page.query_selector('.ais-Pagination-item--nextPage:not(.ais-Pagination-item--disabled) a, a[aria-label="Next page"]')
            if not next_btn:
                print("No active 'Next' button found. Reached the end of pagination.")
                break
                
            print("Clicking 'Next' button...")
            await next_btn.click()
            await asyncio.sleep(8) # wait for Algolia to render new hits
            current_page += 1

        print(f"\nScraping complete. Total new unique books scraped: {total_new_books}")
        if total_new_books > 0:
            apply_styling(excel_file)
            print("Styling applied successfully.")
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
