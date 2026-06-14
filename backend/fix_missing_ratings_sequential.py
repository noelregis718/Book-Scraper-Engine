import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
import sys
import json
import re

EXCEL_FILE = r"E:\Internship\PocketFM\Spencer_Hill_Press.xlsx"

async def process_single_link(page, index, url, title):
    try:
        print(f"[{index}] Navigating to: {title}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Wait for page to settle and check for CAPTCHA
        await asyncio.sleep(2)
        
        for _ in range(3): # Check for CAPTCHA up to 3 times
            if await page.query_selector('#captcha-image, .captcha'):
                print(f"\n[!!! ACTION REQUIRED !!!] CAPTCHA detected for '{title}'! Please solve it in the browser window.")
                await page.wait_for_selector('.BookPageMetadataSection__genre, .RatingStatistics__rating, [data-testid="description"]', timeout=300000)
                await asyncio.sleep(2)
            else:
                break
                
        # Extract data manually to avoid the Execution context error in the class
        avg_rating = "N/A"
        rating_count = "N/A"
        primary = "1"
        
        ld_el = await page.query_selector('script[type="application/ld+json"]')
        if ld_el:
            try:
                ld_data = json.loads(await ld_el.inner_text())
                if isinstance(ld_data, list): ld_data = ld_data[0]
                avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
            except: pass
            
        if avg_rating == "N/A":
            rating_el = await page.query_selector('.RatingStatistics__rating')
            if rating_el: avg_rating = await rating_el.inner_text()
            
        if rating_count == "N/A":
            count_el = await page.query_selector('[data-testid="ratingsCount"]')
            if count_el:
                c = await count_el.inner_text()
                rating_count = c.split()[0].replace(',', '')
                
        # Series check
        series_link = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
        if series_link:
            series_url = await series_link.evaluate("el => el.href")
            try:
                await page.goto(series_url, wait_until="domcontentloaded", timeout=45000)
                content = await page.content()
                m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
                if m: primary = m.group(1)
            except: pass
            
        return index, avg_rating, rating_count, primary
    except Exception as e:
        print(f"[{index}] Error extracting {title}: {e}")
    return index, "N/A", "N/A", "1"

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
        
        page = await context.new_page()
        
        results = []
        for idx, url, title in missing_indices:
            res = await process_single_link(page, idx, url, title)
            print(f"-> Extracted: Rating: {res[1]}, Count: {res[2]}")
            results.append(res)
            
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
