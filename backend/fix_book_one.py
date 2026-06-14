import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
import json

EXCEL_FILE = r"E:\Internship\PocketFM\Spencer_Hill_Press.xlsx"

async def scrape_book(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Navigating to {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Wait for rating element
            await asyncio.sleep(2)
            
            avg_rating = "N/A"
            rating_count = "N/A"
            
            # Extract JSON-LD metadata for reliable rating extraction
            ld_el = await page.query_selector('script[type="application/ld+json"]')
            if ld_el:
                try:
                    ld_data = json.loads(await ld_el.inner_text())
                    if isinstance(ld_data, list): ld_data = ld_data[0]
                    avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                    rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
                except:
                    pass
            
            # Fallback selectors
            if avg_rating == "N/A":
                rating_el = await page.query_selector('.RatingStatistics__rating')
                if rating_el:
                    avg_rating = await rating_el.inner_text()
                    
            if rating_count == "N/A":
                count_el = await page.query_selector('[data-testid="ratingsCount"]')
                if count_el:
                    rating_count = await count_el.inner_text()
                    rating_count = rating_count.split()[0].replace(',', '')
            
            series_num = "1"
            # Try to see if it's a series and get primary books count
            series_link = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
            if series_link:
                series_url = await series_link.evaluate("el => el.href")
                try:
                    await page.goto(series_url, wait_until="domcontentloaded", timeout=45000)
                    content = await page.content()
                    import re
                    m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
                    if m: series_num = m.group(1)
                except:
                    pass
                    
            await browser.close()
            return avg_rating, rating_count, series_num
            
        except Exception as e:
            print(f"Error scraping: {e}")
            await browser.close()
            return "N/A", "N/A", "N/A"

def main():
    df = pd.read_excel(EXCEL_FILE)
    first_url = df.iloc[0]['GoodReads series link']
    
    print(f"First book URL: {first_url}")
    
    avg_rating, rating_count, series_num = asyncio.run(scrape_book(first_url))
    
    print(f"Extracted: Rating: {avg_rating}, Count: {rating_count}, Primary Books: {series_num}")
    
    if avg_rating != "N/A":
        df.at[0, 'Rating (out of 5) of Primary Book 1'] = float(avg_rating) if avg_rating.replace('.','',1).isdigit() else avg_rating
    if rating_count != "N/A":
        df.at[0, 'Ratings (#) of Primary Book 1'] = int(rating_count) if rating_count.isdigit() else rating_count
    df.at[0, 'Number of PRIMARY books in the series'] = series_num
    
    df.to_excel(EXCEL_FILE, index=False)
    print("Updated Excel file!")

if __name__ == '__main__':
    main()
