import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\Spencer_Hill_Press.xlsx"

async def process_single_link(context, scraper, index, url, title):
    page = await context.new_page()
    try:
        print(f"[{index}] Navigating to: {title}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        if await page.query_selector('#captcha-image, .captcha'):
            print(f"\n[!!! ACTION REQUIRED !!!] CAPTCHA detected for '{title}'! Please solve it in the browser window.")
            await page.wait_for_selector('.BookPageMetadataSection__genre, .RatingStatistics__rating, [data-testid="description"]', timeout=300000)
            
        details = await scraper.extract_book_details(page)
        
        if details:
            rating = details.get("GoodReads_Rating", "N/A")
            count = details.get("GoodReads_Rating_Count", "N/A")
            primary = details.get("Num_Primary_Books", "1")
            
            # If missing from json-ld, use fallback series_data
            if rating == "N/A":
                rating = details.get("Book1_Rating", "N/A")
            if count == "N/A":
                count = details.get("Book1_Num_Ratings", "N/A")
                
            return index, rating, count, primary
    except Exception as e:
        print(f"[{index}] Error extracting {title}: {e}")
    finally:
        await page.close()
    return index, "N/A", "N/A", "1"

async def bounded_process(semaphore, context, scraper, index, url, title):
    async with semaphore:
        return await process_single_link(context, scraper, index, url, title)

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    missing_indices = []
    
    for idx, row in df.iterrows():
        rating = str(row['Rating (out of 5) of Primary Book 1']).strip()
        url = str(row['GoodReads series link']).strip()
        
        if (rating == 'nan' or rating == 'N/A' or rating == '') and url.startswith('http'):
            missing_indices.append((idx, url, str(row['Name of Series'])))
            
    print(f"Found {len(missing_indices)} books missing ratings.")
    
    if not missing_indices:
        return
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        scraper = GoodreadsScraper()
        
        # Login to avoid CAPTCHAs
        page = await context.new_page()
        logged_in = await scraper.login_to_goodreads(page)
        await page.close()
        
        semaphore = asyncio.Semaphore(5) # 5 concurrent tabs
        
        tasks = []
        for idx, url, title in missing_indices:
            tasks.append(bounded_process(semaphore, context, scraper, idx, url, title))
            
        print(f"Launching scraper for {len(missing_indices)} missing books...")
        results = await asyncio.gather(*tasks)
        
        await browser.close()
        
    updates = 0
    for idx, rating, count, primary in results:
        if rating != "N/A":
            try:
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = float(rating)
                updates += 1
            except: pass
        if count != "N/A":
            try:
                count_int = int(str(count).replace(',', ''))
                df.at[idx, 'Ratings (#) of Primary Book 1'] = count_int
            except: pass
        if primary != "N/A":
            df.at[idx, 'Number of PRIMARY books in the series'] = primary
            
    print(f"\nSuccessfully updated {updates} books!")
    print(f"Saving to {EXCEL_FILE}...")
    df.to_excel(EXCEL_FILE, index=False)
    print("Done!")

if __name__ == '__main__':
    asyncio.run(main())
