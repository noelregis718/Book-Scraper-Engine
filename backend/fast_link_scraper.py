import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import re
import os

async def get_link(context, title, author):
    page = await context.new_page()
    try:
        # Search Brave for the Goodreads link
        # We search both for book/show and series
        clean_title = re.sub(r'[^\w\s]', '', str(title)).strip()
        query = f'{clean_title} {author} site:goodreads.com'
        url = f"https://search.brave.com/search?q={query.replace(' ', '+')}"
        
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        # Wait a tiny bit for JS to render the search results
        await asyncio.sleep(1) 
        
        links = await page.query_selector_all('a[href*="goodreads.com/book/show/"], a[href*="goodreads.com/series/"]')
        if links:
            href = await links[0].evaluate("el => el.href")
            return href
        return None
    except Exception as e:
        return None
    finally:
        await page.close()

async def worker(worker_id, queue, context, df, lock, total, counter):
    while True:
        try:
            index, title, author = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
            
        link = await get_link(context, title, author)
        
        async with lock:
            counter[0] += 1
            if link:
                df.at[index, 'GoodReads series link'] = link
                print(f"[{counter[0]}/{total}] [Worker {worker_id}] Found: {title} -> {link}")
            else:
                print(f"[{counter[0]}/{total}] [Worker {worker_id}] No link found for: {title}")
                
        queue.task_done()

async def main():
    excel_path = r"e:\Internship\PocketFM\Books_Scraping_Template.xlsx"
    df = pd.read_excel(excel_path, engine='openpyxl')
    
    # Find all rows missing a valid URL
    mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A') | (df['GoodReads series link'] == '') | (~df['GoodReads series link'].astype(str).str.startswith('http'))
    missing = df[mask]
    
    total = len(missing)
    print(f"Missing links to scrape: {total}")
    
    if total == 0:
        print("No missing links. Exiting.")
        return
        
    queue = asyncio.Queue()
    for index, row in missing.iterrows():
        title = row['Name of Series']
        author = row['Author Name']
        if pd.notna(title) and pd.notna(author):
            queue.put_nowait((index, title, author))
            
    excel_lock = asyncio.Lock()
    counter = [0]
    
    async with async_playwright() as p:
        # Use headless true for Brave since it usually doesn't block
        browser = await p.chromium.launch(headless=True)
        # Randomize User Agent slightly to avoid fingerprinting
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Spin up 20 workers for aggressive scraping
        num_workers = 20
        print(f"Starting {num_workers} aggressive workers...")
        workers = [asyncio.create_task(worker(i, queue, context, df, excel_lock, total, counter)) for i in range(num_workers)]
        
        await queue.join()
        
        print("\nAggressive scraping complete! Saving to Excel...")
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        await browser.close()
        print("Done! You're good to go.")

if __name__ == "__main__":
    asyncio.run(main())
