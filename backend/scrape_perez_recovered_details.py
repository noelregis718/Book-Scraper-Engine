import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import json
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import clean_text

EXCEL_FILE = r"E:\Internship\PocketFM\new_books_master_list_perez_literary_scraped.xlsx"
MAX_CONCURRENT = 5

async def scrape_book_details(context, index, url, title, df, semaphore):
    async with semaphore:
        page = await context.new_page()
        safe_title = title.encode('ascii', 'ignore').decode('ascii')
        try:
            print(f"[{index}] Scraping details from URL for '{safe_title}': {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)
            
            avg_rating, rating_count = "N/A", "N/A"
            try:
                ld_el = await page.query_selector('script[type="application/ld+json"]')
                if ld_el:
                    ld_data = json.loads(await ld_el.inner_text())
                    if isinstance(ld_data, list): ld_data = ld_data[0]
                    avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                    rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
            except: pass

            description = "N/A"
            desc_el = await page.query_selector('[data-testid="description"] .Formatted, .readable')
            if desc_el:
                description = clean_text(await desc_el.inner_text())

            series_url = url
            series_link_el = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
            if series_link_el:
                series_url = await series_link_el.evaluate("el => el.href")

            num_primary = "1"
            book1_rating = avg_rating
            book1_ratings = rating_count
            if "/series/" in series_url:
                try:
                    await page.goto(series_url, wait_until="domcontentloaded", timeout=45000)
                    content = await page.content()
                    m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
                    if m: num_primary = m.group(1)
                    row1 = await page.query_selector('.listWithDividers__item, .seriesWork')
                    if row1:
                        rtxt = (await row1.inner_text()).lower()
                        r_match = re.search(r'([\d.]+)\s+avg\s+rating\s+[—\-]\s+([\d,]+)\s+ratings', rtxt)
                        if r_match:
                            book1_rating = r_match.group(1)
                            book1_ratings = r_match.group(2).replace(',', '')
                except: pass

            df.at[index, "GoodReads series link"] = series_url
            df.at[index, "Number of PRIMARY books in the series"] = num_primary
            df.at[index, "Rating (out of 5) of Primary Book 1"] = book1_rating
            df.at[index, "Ratings (#) of Primary Book 1"] = book1_ratings
            df.at[index, "Synopsis (if available)"] = description
            
            print(f"[{index}] Successfully scraped details for '{safe_title}'")
            
        except Exception as e:
            print(f"[{index}] Error scraping '{safe_title}': {e}")
        finally:
            await page.close()

async def run_recovery():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
    
    tasks = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        for idx, row in df.iterrows():
            link = str(row.get('GoodReads series link', '')).strip()
            synopsis = str(row.get('Synopsis (if available)', '')).strip()
            title = str(row.get('Name of Series', '')).strip()
            
            # If we have a link, but synopsis is missing or 'N/A'
            if link and link != 'N/A' and link != 'nan':
                if not synopsis or synopsis == 'N/A' or synopsis == 'nan':
                    tasks.append(scrape_book_details(context, idx, link, title, df, semaphore))
                    
        print(f"Found {len(tasks)} books with links but missing details. Scraping them now...")
        
        if tasks:
            await asyncio.gather(*tasks)
            
        await browser.close()
        
    print("--- Saving Excel ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_recovery())
