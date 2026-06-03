import asyncio
import pandas as pd
import sys
import os
import urllib.parse
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from apply_jra_style import apply_styling
except ImportError:
    def apply_styling(p): pass

EXCEL_FILE = r'E:\Internship\PocketFM\dragonblade_books_combined.xlsx'

async def scrape_author(context, title):
    page = await context.new_page()
    try:
        # Search Goodreads
        query = urllib.parse.quote_plus(title)
        await page.goto(f"https://www.goodreads.com/search?q={query}")
        await page.wait_for_timeout(2000)
        
        # Click first result
        first_result = await page.query_selector('.tableList tr td a.bookTitle')
        if not first_result:
            return "N/A"
            
        href = await first_result.get_attribute("href")
        book_url = f"https://www.goodreads.com{href}" if href.startswith('/') else href
        
        await page.goto(book_url)
        await page.wait_for_timeout(2000)
        
        # Extract author
        author_elem = await page.query_selector('span.ContributorLink__name')
        if author_elem:
            author = await author_elem.inner_text()
            return author.strip()
            
        # fallback
        author_fallback = await page.query_selector('.authorName span[itemprop="name"]')
        if author_fallback:
            author = await author_fallback.inner_text()
            return author.strip()
            
        return "N/A"
    except Exception as e:
        print(f"Error for {title}: {e}")
        return "N/A"
    finally:
        await page.close()

async def worker(context, queue, df, lock, total):
    while True:
        item = await queue.get()
        if item is None:
            break
            
        index, title = item
        print(f"Searching for author: '{title}'")
        
        author = await scrape_author(context, title)
        print(f"Found author for '{title}': {author}")
        
        async with lock:
            df.at[index, "Author Name"] = author
            # Save progressively
            df.to_excel(EXCEL_FILE, index=False)
            
        queue.task_done()

async def main():
    print("Loading excel file...")
    df = pd.read_excel(EXCEL_FILE)
    
    missing = df[df["Author Name"].isna() | (df["Author Name"].astype(str).str.strip() == '') | (df["Author Name"] == 'N/A') | (df["Author Name"] == 'nan')]
    if missing.empty:
        print("No missing authors found!")
        return

    print(f"Found {len(missing)} books missing authors.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        queue = asyncio.Queue()
        for idx, row in missing.iterrows():
            title = str(row.get("Name of Series", ""))
            if title.strip() and title != "nan":
                await queue.put((idx, title))
                
        total = queue.qsize()
        lock = asyncio.Lock()
        
        workers = []
        for _ in range(10): # 10 tabs
            workers.append(asyncio.create_task(worker(context, queue, df, lock, total)))
            
        await queue.join()
        
        for _ in range(10):
            await queue.put(None)
        await asyncio.gather(*workers)
        
        await browser.close()
        
    print("Scraping complete! Reapplying styling...")
    try:
        apply_styling(EXCEL_FILE)
        print("Styling applied successfully.")
    except:
        pass
        
if __name__ == "__main__":
    asyncio.run(main())
