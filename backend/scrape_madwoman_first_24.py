import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"e:\Internship\PocketFM\madwoman_literary_scraped_books.xlsx"
MAX_CONCURRENT = 5

async def process_book(context, scraper, df, idx, title, author, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        print(f"  [Scraping] '{safe_title}' by {safe_author}...")
        
        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                # Update the dataframe
                df.at[idx, 'GoodReads series link'] = data.get('GoodReads_Series_URL') or data.get('GoodReads_Book_URL', 'N/A')
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = data.get('Book1_Rating', data.get('GoodReads_Rating', 'N/A'))
                df.at[idx, 'Ratings (#) of Primary Book 1'] = data.get('Book1_Num_Ratings', data.get('GoodReads_Rating_Count', 'N/A'))
                df.at[idx, 'Synopsis (if available)'] = data.get('Description', 'N/A')
                print(f"  [Done] '{safe_title}'")
            else:
                print(f"  [Not Found] '{safe_title}'")
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"  [Error] '{safe_title}': {err_msg}")

async def run_scrape():
    df = pd.read_excel(EXCEL_FILE)
    
    # Extract only the first 24 books
    tasks_to_run = []
    
    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        print("[System] Logging in to Goodreads...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        
        # We only process the first 24 rows
        print("--- Processing First 24 Books ---")
        for idx in range(min(24, len(df))):
            title = str(df.at[idx, 'Name of Series']).strip()
            author = str(df.at[idx, 'Author Name']).strip()
            if title and title.lower() != 'nan':
                tasks_to_run.append(process_book(context, scraper, df, idx, title, author, semaphore))
        
        await asyncio.gather(*tasks_to_run)
        
        await browser.close()
        
    print("--- Rebuilding Excel File with new data ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from format_madwoman import format_madwoman
        format_madwoman(EXCEL_FILE, EXCEL_FILE)
    except Exception as e:
        print(f"[Warning] Could not reapply style: {e}")
        
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
