import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright

FILE_PATH = r"e:\Internship\PocketFM\Romantasy_v2_extracted.xlsx"

async def solve_captcha_if_present(page, url=""):
    try:
        if await page.query_selector('#captcha-image, .captcha, iframe[src*="captcha"]'):
            print(f"    [!!!] CAPTCHA detected! Please solve it manually.")
            try:
                await page.wait_for_selector('a.bookTitle, h1', timeout=120000)
                print(f"    [Success] CAPTCHA solved.")
            except:
                print(f"    [Timeout] CAPTCHA wait timeout.")
    except Exception:
        pass

async def search_book_on_goodreads(page, title, author):
    search_term = f"{title} {author}".strip()
    if not search_term:
        return None
        
    search_url = f"https://www.goodreads.com/search?q={search_term.replace(' ', '+')}"
    print(f"    Searching Goodreads: {search_url}")
    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        await solve_captcha_if_present(page, search_url)
        
        # Click the first book result
        first_result = await page.query_selector('a.bookTitle')
        if first_result:
            b_url = await first_result.evaluate("el => el.href")
            if b_url.startswith('/'):
                b_url = f"https://www.goodreads.com{b_url}"
            return b_url
    except Exception as e:
        print(f"    Error searching for {search_term}: {e}")
    return None

async def process_row(index, row, context, df, semaphore, excel_lock):
    book1_link = str(row.get('GR Book 1 link', '')).strip()
    title = str(row.get('Title', '')).strip()
    author = str(row.get('Author Name', '')).strip()
    
    # Check if GR Book 1 link is missing
    is_missing = book1_link == '' or book1_link.lower() == 'nan' or not book1_link.startswith('http')
    
    if not is_missing:
        return
        
    if title == '' or title.lower() == 'nan':
        return
        
    async with semaphore:
        print(f"\n[Row {index}] Missing GR Book 1 link. Title: '{title}'")
        page = await context.new_page()
        try:
            found_link = await search_book_on_goodreads(page, title, author)
            if found_link:
                print(f"  [Row {index}] Found Book 1 Link: {found_link}")
                async with excel_lock:
                    df.at[index, 'GR Book 1 link'] = found_link
            else:
                print(f"  [Row {index}] No results found.")
                
            async with excel_lock:
                df.to_excel(FILE_PATH, index=False)
                
        except Exception as e:
            print(f"  [Row {index}] Failed to process: {e}")
        finally:
            await page.close()

async def main():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return
        
    print(f"Loading {FILE_PATH}...")
    df = pd.read_excel(FILE_PATH, header=0) 
    
    if 'GR Book 1 link' not in df.columns:
        print("Error: 'GR Book 1 link' column not found.")
        return
        
    semaphore = asyncio.Semaphore(8)
    excel_lock = asyncio.Lock()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        print("Starting concurrent scrape for missing Book 1 links...")
        
        tasks = []
        for index, row in df.iterrows():
            tasks.append(process_row(index, row, context, df, semaphore, excel_lock))
            
        await asyncio.gather(*tasks)
        await browser.close()
    
    df.to_excel(FILE_PATH, index=False)
    print(f"Scraping fully complete. Saved to {FILE_PATH}")

if __name__ == "__main__":
    asyncio.run(main())
