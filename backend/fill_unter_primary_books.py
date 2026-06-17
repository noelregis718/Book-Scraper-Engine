import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import re

EXCEL_FILE = "e:/Internship/PocketFM/unter_agency_books.xlsx"

async def process_row(context, df, index, book_url):
    page = await context.new_page()
    try:
        print(f"[{index}] Visiting: {book_url}")
        await page.goto(book_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
        # Look for series link
        series_link = ""
        series_elem = await page.query_selector('h3.Text__h3 a')
        if series_elem:
            href = await series_elem.get_attribute('href')
            if href and "series" in href:
                series_link = href
                
        if not series_link:
            print(f"[{index}] No series found. Standalone book -> 1")
            df.at[index, 'Number of PRIMARY books in the series'] = 1
            await page.close()
            return
            
        full_series_link = series_link if series_link.startswith('http') else f"https://www.goodreads.com{series_link}"
        print(f"[{index}] Found series link! Visiting: {full_series_link}")
        
        await page.goto(full_series_link, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
        series_desc_elem = await page.query_selector('div.responsiveSeriesHeader__subtitle')
        if series_desc_elem:
            desc = await series_desc_elem.inner_text()
            match = re.search(r'(\d+)\s+primary\s+works', desc, re.IGNORECASE)
            if match:
                num_primary_books = match.group(1)
                df.at[index, 'Number of PRIMARY books in the series'] = int(num_primary_books)
                print(f"[{index}] Success! Found {num_primary_books} primary books.")
            else:
                print(f"[{index}] Could not parse primary works string: {desc}")
                df.at[index, 'Number of PRIMARY books in the series'] = 1
        else:
            print(f"[{index}] Could not find series subtitle.")
            df.at[index, 'Number of PRIMARY books in the series'] = 1
            
    except Exception as e:
        print(f"[{index}] Error processing {book_url}: {e}")
        df.at[index, 'Number of PRIMARY books in the series'] = 1
    finally:
        await page.close()

async def main():
    df = pd.read_excel(EXCEL_FILE)
    
    if 'Number of PRIMARY books in the series' not in df.columns:
        df['Number of PRIMARY books in the series'] = pd.NA
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        while True:
            batch = []
            for index, row in df.iterrows():
                url = row.get('GoodReads series link')
                if pd.isna(url) or str(url).strip() == "":
                    continue
                    
                val = row.get('Number of PRIMARY books in the series')
                if pd.notna(val) and str(val).strip() != "" and str(val).strip() != "nan":
                    continue
                    
                batch.append((index, str(url)))
                if len(batch) == 10:
                    break
                    
            if not batch:
                print("All rows with URLs have primary books filled!")
                break
                
            print(f"\n--- Starting batch of {len(batch)} books ---")
            tasks = []
            for index, url in batch:
                tasks.append(process_row(context, df, index, url))
                
            await asyncio.gather(*tasks)
            
            df.to_excel(EXCEL_FILE, index=False)
            print("Batch saved to excel!")
            
        await browser.close()

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())
