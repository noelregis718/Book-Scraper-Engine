import asyncio
import os
import sys
import pandas as pd
import json
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from format_madwoman import format_madwoman

EXCEL_FILE = r"e:\Internship\PocketFM\madwoman_literary_scraped_books.xlsx"
STATE_FILE = r"e:\Internship\PocketFM\backend\madwoman_state.json"
MAX_CONCURRENT = 5

async def aggressive_search(context, title, author, semaphore):
    async with semaphore:
        page = await context.new_page()
        try:
            safe_title = str(title).encode('ascii', 'ignore').decode('ascii')
            safe_author = str(author).encode('ascii', 'ignore').decode('ascii')
            
            # 1. Search Brave directly
            query = f'"{safe_title}" {safe_author} site:goodreads.com'
            url = f"https://search.brave.com/search?q={query.replace(' ', '+')}"
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Extract links
            links = await page.query_selector_all('a[href*="goodreads.com/book/show/"], a[href*="goodreads.com/series/"]')
            if links:
                found_url = await links[0].evaluate("el => el.href")
                print(f"  [Found Link] {safe_title} -> {found_url}")
                return found_url
            
            # 2. Try internal Goodreads search if Brave fails
            print(f"  [Fallback Search] {safe_title}...")
            await page.goto(f"https://www.goodreads.com/search?q={safe_title.replace(' ', '+')}+{safe_author.replace(' ', '+')}", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(1.5)
            gl_links = await page.query_selector_all('a.bookTitle, [data-testid="bookSearchResult"] a')
            if gl_links:
                found_url = await gl_links[0].evaluate("el => el.href")
                print(f"  [Found Link Goodreads] {safe_title} -> {found_url}")
                return found_url
                
            print(f"  [Not Found] {safe_title}")
            return ''
        except Exception as e:
            print(f"  [Error] {str(title).encode('ascii', 'ignore').decode('ascii')}: {e}")
            return ''
        finally:
            await page.close()

async def run_fix():
    df = pd.read_excel(EXCEL_FILE)
    
    # Load state
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
            
    tasks = []
    indices_to_update = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        for idx, row in df.iterrows():
            link = row.get('GoodReads series link')
            if pd.isna(link) or link == '' or str(link).strip() == 'N/A':
                title = row.get('Name of Series')
                author = row.get('Author Name')
                if pd.isna(title) or not str(title).strip() or str(title).lower() == 'nan':
                    continue
                
                title_str = str(title).strip()
                author_str = str(author).strip()
                
                # Check state first!
                found_in_state = False
                if author_str in state:
                    for b in state[author_str]:
                        if b.get('title') == title_str or b.get('Book_Title') == title_str:
                            st_link = b.get('GoodReads_Series_URL')
                            if not st_link or st_link == 'N/A':
                                st_link = b.get('GoodReads_Book_URL')
                            if st_link and st_link != 'N/A':
                                df.at[idx, 'GoodReads series link'] = st_link
                                print(f"[Restored from State] {title_str} -> {st_link}")
                                found_in_state = True
                                break
                                
                if not found_in_state:
                    tasks.append(aggressive_search(context, title_str, author_str, semaphore))
                    indices_to_update.append(idx)
                    
        print(f"Needs aggressive search: {len(tasks)} books")
        
        if tasks:
            results = await asyncio.gather(*tasks)
            for idx, res_url in zip(indices_to_update, results):
                if res_url:
                    df.at[idx, 'GoodReads series link'] = res_url
                    
        await browser.close()
        
    print("--- Saving Excel ---")
    df.to_excel(EXCEL_FILE, index=False)
    format_madwoman(EXCEL_FILE, EXCEL_FILE)
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_fix())
