import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright

CONCURRENCY = 3

async def get_author_from_goodreads(context, url):
    if not url or url.lower() in ["", "nan", "n/a"]:
        return ""
    
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
        # Try finding author name using common Goodreads selectors
        author_el = await page.query_selector('[data-testid="authorName"], .authorName__container [itemprop="name"], .authorName')
        if author_el:
            author = await author_el.inner_text()
            return author.strip()
            
    except Exception as e:
        print(f"    [Error] navigating to {url}: {e}")
    finally:
        await page.close()
        
    return ""

async def process_row(context, df, idx, semaphore, excel_path, file_lock):
    async with semaphore:
        title = str(df.at[idx, "Name of Series"]).strip()
        url = str(df.at[idx, "GoodReads series link"]).strip()
        
        print(f"  [Scraping Author] '{title}' -> {url}")
        
        author_found = await get_author_from_goodreads(context, url)
        
        if author_found:
            df.at[idx, "Author Name"] = author_found
            print(f"  [OK] Found Author: {author_found} for '{title}'")
        else:
            print(f"  [Failed] Could not find author for '{title}'")
            
        async with file_lock:
            try:
                df.to_excel(excel_path, index=False)
            except Exception as e:
                pass

async def scrape_missing_authors(excel_path):
    print(f"Loading: {excel_path}")
    df = pd.read_excel(excel_path, keep_default_na=False)
    
    # Identify rows missing authors
    missing_mask = df["Author Name"].astype(str).str.lower().str.strip().isin(['nan', '', 'unknown', '[author name to be fetched]', 'n/a'])
    
    rows_to_process = df[missing_mask].index.tolist()
    print(f"Missing authors to scrape: {len(rows_to_process)}\n")
    
    if not rows_to_process:
        print("No missing authors found!")
        return

    file_lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        tasks = [
            process_row(context, df, idx, semaphore, excel_path, file_lock)
            for idx in rows_to_process
        ]
        await asyncio.gather(*tasks)

        print("\nAuthor scraping complete!")
        await browser.close()

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base, "Stonesong_Books.xlsx")
    asyncio.run(scrape_missing_authors(excel_path))
