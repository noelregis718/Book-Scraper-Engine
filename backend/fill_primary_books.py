import asyncio
import pandas as pd
import urllib.parse
from playwright.async_api import async_playwright
import re

EXCEL_FILE = "e:/Internship/PocketFM/books_from_images.xlsx"

async def extract_primary_books(context, df, index, title):
    page = await context.new_page()
    try:
        query = f'"{title}" series site:goodreads.com/series'
        print(f"[{index}] Searching DDG for series: {title}")
        ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
        
        await page.goto(ddg_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
        html = await page.content()
        # Look for 'primary works'
        match = re.search(r'(\d+)\s+primary\s+works?', html, re.IGNORECASE)
        if match:
            num_books = int(match.group(1))
            print(f"[{index}] Found: {num_books} primary works")
            df.at[index, 'Number of PRIMARY books in the series'] = num_books
        else:
            print(f"[{index}] Not found (might not be a series).")
            # We can put a space or 0 to indicate it was checked but nothing found
            df.at[index, 'Number of PRIMARY books in the series'] = 0
            
    except Exception as e:
        print(f"[{index}] Error: {e}")
    finally:
        await page.close()


async def main():
    print("Loading excel file...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Identify missing rows
    missing_indices = []
    for index, row in df.iterrows():
        val = row.get('Number of PRIMARY books in the series')
        if pd.isna(val) or str(val).strip() == "" or val == "nan":
            missing_indices.append(index)
            
    print(f"Found {len(missing_indices)} rows with missing primary books data.")
    
    if not missing_indices:
        print("Nothing to do!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        batch_size = 6
        for i in range(0, len(missing_indices), batch_size):
            batch = missing_indices[i:i+batch_size]
            print(f"\n--- Starting new batch of {len(batch)} series concurrently ---")
            
            tasks = []
            for index in batch:
                title = str(df.at[index, 'Name of Series'])
                tasks.append(extract_primary_books(context, df, index, title))
                
            await asyncio.gather(*tasks)
            
            # Save after every batch
            df.to_excel(EXCEL_FILE, index=False)
            print("Batch complete and saved to Excel!")
            
        await browser.close()
        print("Finished filling all missing series data!")

if __name__ == "__main__":
    asyncio.run(main())
