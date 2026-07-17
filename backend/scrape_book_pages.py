import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def run_scraper():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(workspace_dir, "Small_Publishers_Crime_Scraped.xlsx")

    print(f"Loading input file: {input_path}")
    if not os.path.exists(input_path):
        print("Input file not found.")
        return

    df = pd.read_excel(input_path)
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await scraper.login_to_goodreads(page)
        
        for index, row in df.iterrows():
            title = str(row.get("Book 1 Title", "")).strip()
            author = str(row.get("Author Name", "")).strip()
            existing_pages = str(row.get("Number of Pages in Book 1", "")).strip()
            
            if not title or title.lower() == 'nan':
                continue
                
            if existing_pages and existing_pages.lower() != 'nan' and existing_pages != 'None':
                if re.match(r'^\d+$', existing_pages):
                    continue
                
            print(f"\n[{index + 1}/{len(df)}] Scraping page count for: '{title}' by '{author}'", flush=True)
            
            try:
                # Use our robust scraper to find the book
                data = await scraper.scrape_goodreads_data(context, title=title, author=author)
                book_url = data.get("GoodReads_Book_URL")
                
                if not book_url:
                    print("  [Failed] Could not find book URL.")
                    continue
                    
                # Navigate to the specific book URL
                await page.goto(book_url, timeout=45000, wait_until="domcontentloaded")
                
                try:
                    await page.wait_for_selector("p[data-testid='pagesFormat']", timeout=15000)
                    pages_element = await page.query_selector("p[data-testid='pagesFormat']")
                    if pages_element:
                        pages_text = await pages_element.inner_text()
                        match = re.search(r'(\d+)\s*pages', pages_text, re.IGNORECASE)
                        if match:
                            num_pages = match.group(1)
                            df.at[index, "Number of Pages in Book 1"] = num_pages
                            print(f"  [Success] Found {num_pages} pages.")
                        else:
                            print(f"  [Failed] Could not parse page count from text: '{pages_text}'")
                    else:
                        print("  [Failed] Could not find pages element on the book page.")
                except Exception as e:
                    print(f"  [Failed] Timeout waiting for pagesFormat element.")
                    
            except Exception as e:
                print(f"  [Error] Failed to process '{title}': {e}")
                
            # Auto-save after each book
            df.to_excel(input_path, index=False)
            
        await browser.close()
        
    print(f"\nScraping complete. Final dataset saved to {input_path}")

if __name__ == "__main__":
    asyncio.run(run_scraper())
