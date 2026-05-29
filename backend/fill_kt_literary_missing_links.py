import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import urllib.parse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\KT_Literary_Merged_Formatted.xlsx"
MAX_CONCURRENT = 3 

async def aggressive_search(context, title, author, semaphore):
    async with semaphore:
        page = await context.new_page()
        try:
            safe_title = str(title).encode('ascii', 'ignore').decode('ascii')
            safe_author = str(author).encode('ascii', 'ignore').decode('ascii')
            
            # 1. Try Bing Search
            query = f'"{safe_title}" {safe_author} site:goodreads.com/book'
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.bing.com/search?q={encoded_query}"
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Extract links from Bing
            links = await page.query_selector_all('a[href*="goodreads.com/book/show/"]')
            if links:
                found_url = await links[0].evaluate("el => el.href")
                print(f"  [Found Link via Bing] {safe_title} -> {found_url}")
                return found_url
                
            # 2. Try Yahoo Search (Fallback)
            print(f"  [Fallback to Yahoo] {safe_title}...")
            url2 = f"https://search.yahoo.com/search?p={encoded_query}"
            await page.goto(url2, wait_until="domcontentloaded", timeout=30000)
            
            links2 = await page.query_selector_all('a[href*="goodreads.com/book/show/"]')
            if links2:
                found_url = await links2[0].evaluate("el => el.href")
                print(f"  [Found Link via Yahoo] {safe_title} -> {found_url}")
                return found_url

            print(f"  [Not Found Anywhere] {safe_title}")
            return ''
        except Exception as e:
            print(f"  [Error] {str(title).encode('ascii', 'ignore').decode('ascii')}: {e}")
            return ''
        finally:
            await page.close()

async def run_fix():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
            
    tasks = []
    indices_to_update = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        for idx, row in df.iterrows():
            link = row.get('GoodReads series link')
            if pd.isna(link) or link == '' or str(link).strip() == 'N/A' or str(link).strip() == 'nan':
                title = row.get('Name of Series')
                author = row.get('Author Name')
                if pd.isna(title) or not str(title).strip() or str(title).lower() == 'nan':
                    continue
                
                title_str = str(title).strip()
                author_str = str(author).strip()
                
                tasks.append(aggressive_search(context, title_str, author_str, semaphore))
                indices_to_update.append(idx)
                    
        print(f"Needs deep search via Bing/Yahoo: {len(tasks)} books")
        
        if tasks:
            results = await asyncio.gather(*tasks)
            for idx, res_url in zip(indices_to_update, results):
                if res_url:
                    df.at[idx, 'GoodReads series link'] = res_url
                    
        await browser.close()
        
    print("--- Saving Excel ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    print("ALL DONE FINDING LINKS WITH DEEP SEARCH!")

if __name__ == '__main__':
    asyncio.run(run_fix())
