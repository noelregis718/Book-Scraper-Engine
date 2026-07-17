import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def process_row(index, row, df, context, semaphore, excel_path, lock, scraper):
    title = str(row.get("Book 1 Title", "")).strip()
    author = str(row.get("Author Name", "")).strip()
    existing_pages = str(row.get("Number of Pages in Book 1", "")).strip()
    
    if not title or title.lower() == 'nan':
        return
        
    # Skip if we already scraped it
    if existing_pages and existing_pages.lower() != 'nan' and existing_pages != 'None':
        if re.match(r'^\d+(\.\d+)?$', existing_pages):
            return

    async with semaphore:
        print(f"[{index+1}] Searching for Book: '{title}' by '{author}'", flush=True)
        try:
            # 1. Search for the book to get its URL using the existing robust scraper search method
            data = await scraper.scrape_goodreads_data(context, title=title, author=author)
            
            if data:
                # 2. Extract page count by going directly to the Book URL
                book_url = data.get("GoodReads_Book_URL")
                num_pages = None
                
                if book_url and book_url != "N/A":
                    page = await context.new_page()
                    try:
                        print(f"  [{index+1}] Found URL. Navigating to Book Page to scrape pages...", flush=True)
                        await page.goto(book_url, wait_until="domcontentloaded", timeout=90000)
                        
                        # Aggressively navigate to Book 1 if we landed on a Series page
                        if "/series/" in page.url:
                            print(f"  [{index+1}] Landed on series page, finding Book 1...", flush=True)
                            book_links = await page.query_selector_all('a[href*="/book/show/"]')
                            actual_book_url = None
                            for link in book_links:
                                href = await link.evaluate("el => el.href")
                                if re.search(r'/show/\d+', href):
                                    actual_book_url = href
                                    break
                            if not actual_book_url and book_links:
                                actual_book_url = await book_links[0].evaluate("el => el.href")
                            if actual_book_url:
                                await page.goto(actual_book_url, wait_until="domcontentloaded", timeout=90000)
                                await asyncio.sleep(2)
                        
                        # Scroll to trigger lazy loading of page count elements
                        await page.evaluate("window.scrollBy(0, 1000)")
                        await asyncio.sleep(1)
                        await page.evaluate("window.scrollBy(0, 1000)")
                        await asyncio.sleep(1)
                        
                        content = await page.content()
                        soup = BeautifulSoup(content, 'html.parser')
                        text = soup.get_text(separator=' ')
                        
                        matches = re.findall(r'(\d+)\s*pages', text, re.IGNORECASE)
                        for m in matches:
                            if 10 < int(m) < 4000:
                                num_pages = m
                                break
                    except Exception as e:
                        print(f"  [{index+1}] Warning: Failed to extract pages for '{title}': {e}", flush=True)
                    finally:
                        await page.close()

                # 3. Save ONLY the page count to DataFrame safely
                if num_pages:
                    async with lock:
                        df.at[index, "Number of Pages in Book 1"] = float(num_pages)
                        df.to_excel(excel_path, index=False)
                    print(f"  [{index+1}] Success for '{title}'. Pages: {num_pages}", flush=True)
                else:
                    print(f"  [{index+1}] Could not find page count for '{title}'.", flush=True)
            else:
                print(f"  [{index+1}] Failed to find book on Goodreads: '{title}'", flush=True)
        except Exception as e:
            print(f"  [{index+1}] Error for '{title}': {e}", flush=True)

async def run_scraper():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(workspace_dir, "Small_Mid_Sized_Publishers_Crime_Series_Expanded_30_Per_Publisher.xlsx")
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    df = pd.read_excel(input_path)
    
    # Fix pandas incompatible dtype issue when assigning strings/floats to NaN
    if "Number of Pages in Book 1" in df.columns:
        df["Number of Pages in Book 1"] = df["Number of Pages in Book 1"].astype(object)
    else:
        df["Number of Pages in Book 1"] = ""
    
    # Allow 4 tabs at once to reduce timeout crashes
    semaphore = asyncio.Semaphore(4)
    lock = asyncio.Lock()
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Login first so we have cookies for all tabs
        page = await context.new_page()
        await scraper.login_to_goodreads(page)
        await page.close()
        
        tasks = []
        for index, row in df.iterrows():
            tasks.append(process_row(index, row, df, context, semaphore, input_path, lock, scraper))
            
        print(f"\nStarting aggressive page count scraper for {len(df)} books...", flush=True)
        await asyncio.gather(*tasks)
        
        await browser.close()
        
    print("\nScraping complete. Final dataset saved.", flush=True)

if __name__ == "__main__":
    asyncio.run(run_scraper())
