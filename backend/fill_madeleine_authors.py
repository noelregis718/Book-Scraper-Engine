import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from format_madwoman import format_madwoman
import re

EXCEL_FILE = r"e:\Internship\PocketFM\madeleine_milburn_combined.xlsx"
MAX_CONCURRENT = 5
MAX_ROWS = 106

async def get_author_from_url(context, url, title, idx, df, semaphore):
    async with semaphore:
        page = await context.new_page()
        try:
            print(f"  [Scraping Author] {title} at {url}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            author_found = ""
            author_el = await page.query_selector('[data-testid="authorName"], .authorName__container [itemprop="name"], .authorName')
            if author_el:
                author_found = await author_el.inner_text()
                author_found = str(author_found).strip()
            
            if author_found:
                df.at[idx, 'Author Name'] = author_found
                print(f"  [Found] {title} -> {author_found}")
            else:
                print(f"  [Not Found] {title}")
                
        except Exception as e:
            print(f"  [Error] {title}: {e}")
        finally:
            await page.close()

async def run_fix():
    df = pd.read_excel(EXCEL_FILE)
    
    tasks = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        print(f"--- Processing First {MAX_ROWS} Books for missing Authors ---")
        for idx in range(min(MAX_ROWS, len(df))):
            author = str(df.at[idx, 'Author Name']).strip()
            title = str(df.at[idx, 'Name of Series']).strip()
            link = str(df.at[idx, 'GoodReads series link']).strip()
            
            # If author is missing and we have a valid link, go get it!
            if (not author or author.lower() == 'nan') and link and 'goodreads.com' in link:
                tasks.append(get_author_from_url(context, link, title, idx, df, semaphore))
        
        if tasks:
            await asyncio.gather(*tasks)
            
        await browser.close()
        
    print("--- Saving Excel ---")
    df.to_excel(EXCEL_FILE, index=False)
    format_madwoman(EXCEL_FILE, EXCEL_FILE)
    
    # Copy to downloads aggressively
    os.system(r'powershell -Command "Copy-Item e:\Internship\PocketFM\madeleine_milburn_combined.xlsx -Destination C:\Users\noelr\Downloads\madeleine_milburn_combined.xlsx -Force"')
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_fix())
