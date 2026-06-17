import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format.xlsx')
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)

    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        await scraper.login_to_goodreads(page)
        
        missing_indices = df.index[(df['GoodReads series link'].isna()) | (df['GoodReads series link'] == 'N/A') | (df['GoodReads series link'] == '')].tolist()
        print(f"\nFound {len(missing_indices)} books missing Goodreads links. Starting aggressive link scraper...")
        
        for idx in missing_indices:
            title = str(df.at[idx, 'Name of Series'])
            author = str(df.at[idx, 'Author Name']) if pd.notna(df.at[idx, 'Author Name']) else ""
            
            print(f"\n[Scraping Link] {title} by {author}")
            query = f"{title} {author}".strip()
            
            try:
                search_url = f"https://www.goodreads.com/search?q={query.replace(' ', '+')}"
                await page.goto(search_url, wait_until="domcontentloaded")
                await asyncio.sleep(2)
                
                # Grab the first book link
                first_link = await page.query_selector('a.bookTitle, [data-testid="bookTitle"] a')
                if first_link:
                    book_url = await first_link.evaluate("el => el.href")
                    # Remove query params to make the link clean
                    clean_url = book_url.split('?')[0]
                    
                    df.at[idx, 'GoodReads series link'] = clean_url
                    print(f"  -> Found Link: {clean_url}")
                else:
                    print(f"  -> Could not find link for {title}")
                    
            except Exception as e:
                print(f"  -> Error scraping {title}: {e}")
                
            # Auto-save
            df.to_excel(excel_path, index=False)
            
        print("\n--- Scrape Complete! Excel file updated. ---")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
