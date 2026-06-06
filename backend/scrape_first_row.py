import asyncio
import os
import sys
import pandas as pd
import re
import json
import urllib.parse
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import clean_text

EXCEL_FILE = r"E:\Internship\PocketFM\books_authors_latest_batch.xlsx"

async def scrape_first_row():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    df = df.fillna("")
    
    if df.empty:
        print("Excel file is empty.")
        return
        
    index = 0
    title = str(df.at[index, "Name of Series"]).strip()
    author = str(df.at[index, "Author Name"]).strip()
    
    print(f"Targeting first row: {title} by {author}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        try:
            query = f"{title} {author}".strip()
            search_url = f"https://www.goodreads.com/search?q={urllib.parse.quote_plus(query)}"
            
            print(f"Searching for: {query}")
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)
            
            book_url = ""
            current_url = page.url
            if "/book/show/" in current_url:
                book_url = current_url
            else:
                el = await page.query_selector('a.bookTitle, [data-testid="bookTitle"] a, h3 a[href*="/book/show/"]')
                if el:
                    book_url = await el.evaluate("el => el.href")
            
            if not book_url:
                print("Could not find book link.")
            else:
                if book_url != current_url:
                    await page.goto(book_url, wait_until="domcontentloaded", timeout=45000)
                    await asyncio.sleep(2)
                    
                # Synopsis
                desc_el = await page.query_selector('[data-testid="description"] .Formatted, .readable')
                if desc_el:
                    synopsis = clean_text(await desc_el.inner_text())
                    df.at[index, "Synopsis (if available)"] = synopsis
                
                # Rating & Count
                try:
                    ld_el = await page.query_selector('script[type="application/ld+json"]')
                    if ld_el:
                        ld_data = json.loads(await ld_el.inner_text())
                        if isinstance(ld_data, list): ld_data = ld_data[0]
                        rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                        count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
                        
                        df.at[index, "Rating (out of 5) of Primary Book 1"] = rating
                        df.at[index, "Ratings (#) of Primary Book 1"] = count
                except:
                    pass
                    
                # Series Info
                series_link_el = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
                if series_link_el:
                    series_url = await series_link_el.evaluate("el => el.href")
                    df.at[index, "GoodReads series link"] = series_url
                    
                    try:
                        await page.goto(series_url, wait_until="domcontentloaded", timeout=45000)
                        content = await page.content()
                        m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
                        if m:
                            df.at[index, "Number of PRIMARY books in the series"] = m.group(1)
                        
                        row1 = await page.query_selector('.listWithDividers__item, .seriesWork')
                        if row1:
                            rtxt = (await row1.inner_text()).lower()
                            r_match = re.search(r'([\d.]+)\s+avg\s+rating\s+[—\-]\s+([\d,]+)\s+ratings', rtxt)
                            if r_match:
                                df.at[index, "Rating (out of 5) of Primary Book 1"] = r_match.group(1)
                                df.at[index, "Ratings (#) of Primary Book 1"] = r_match.group(2).replace(',', '')
                    except:
                        pass
                else:
                    df.at[index, "GoodReads series link"] = book_url
                    df.at[index, "Number of PRIMARY books in the series"] = "1"
                    
                print(f"Scraped successfully: {title}")
                
        except Exception as e:
            print(f"Error: {e}")
            
        await browser.close()
        
    print(f"Saving to {EXCEL_FILE}...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
    except:
        pass
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("All done!")

if __name__ == '__main__':
    asyncio.run(scrape_first_row())
