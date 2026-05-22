import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from format_madwoman import format_madwoman

EXCEL_FILE = r"e:\Internship\PocketFM\madeleine_milburn_combined.xlsx"
MAX_CONCURRENT = 5
MAX_ROWS = 106

async def get_author_via_brave(context, title, idx, df, semaphore):
    async with semaphore:
        page = await context.new_page()
        try:
            safe_title = title.encode('ascii', 'ignore').decode('ascii')
            query = f'"{safe_title}" site:goodreads.com/book/show/'
            url = f"https://search.brave.com/search?q={query.replace(' ', '+')}"
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Find the title of the first search result
            title_el = await page.query_selector('.snippet-title')
            if title_el:
                res_title = await title_el.inner_text()
                # Usually: "Book Title by Author Name - Goodreads" or "Book Title by Author Name"
                if ' by ' in res_title:
                    author_part = res_title.split(' by ')[-1]
                    # Clean up
                    author_part = author_part.split(' - ')[0].split(' | ')[0].split(' -')[0].strip()
                    
                    df.at[idx, 'Author Name'] = author_part
                    print(f"  [Found Author] {safe_title} -> {author_part}")
                else:
                    print(f"  [No 'by' in title] {safe_title} ({res_title})")
            else:
                print(f"  [Not Found] {safe_title}")
                
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
        
        print(f"--- Fast Brave Search for Authors ---")
        for idx in range(min(MAX_ROWS, len(df))):
            author = str(df.at[idx, 'Author Name']).strip()
            title = str(df.at[idx, 'Name of Series']).strip()
            
            # If author is missing
            if (not author or author.lower() == 'nan') and title and title.lower() != 'nan':
                tasks.append(get_author_via_brave(context, title, idx, df, semaphore))
        
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
