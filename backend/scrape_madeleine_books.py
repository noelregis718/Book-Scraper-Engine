import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"e:\Internship\PocketFM\madeleine_milburn_combined.xlsx"
MAX_CONCURRENT = 5
MAX_ROWS = 106

async def process_book(context, scraper, df, idx, title, author, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        print(f"  [Scraping] '{safe_title}' by {safe_author}...")
        
        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                # Get links - aggressively prefer Book URL if Series URL is missing or "N/A"
                link = data.get('GoodReads_Series_URL')
                if not link or link == 'N/A':
                    link = data.get('GoodReads_Book_URL', 'N/A')
                if link == 'N/A': link = ''
                    
                df.at[idx, 'GoodReads series link'] = link
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                
                # Fix ratings fallback
                rating = data.get('Book1_Rating', 'N/A')
                if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = rating
                
                count = data.get('Book1_Num_Ratings', 'N/A')
                if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                df.at[idx, 'Ratings (#) of Primary Book 1'] = count
                
                df.at[idx, 'Synopsis (if available)'] = data.get('Description', 'N/A')
                df.at[idx, 'Romantasy = Yes or No?'] = data.get('Romantasy_Subgenre', 'No')
                
                print(f"  [Done] '{safe_title}'")
            else:
                print(f"  [Not Found] '{safe_title}'")
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"  [Error] '{safe_title}': {err_msg}")

async def run_scrape():
    df = pd.read_excel(EXCEL_FILE)
    
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
        
        print(f"--- Processing First {MAX_ROWS} Books ---")
        for idx in range(min(MAX_ROWS, len(df))):
            link = str(df.at[idx, 'GoodReads series link']).strip()
            # Skip if we already got it
            if link and link.lower() != 'nan' and link != 'N/A' and 'goodreads.com' in link:
                continue
                
            title = str(df.at[idx, 'Name of Series']).strip()
            author = str(df.at[idx, 'Author Name']).strip()
            
            if author.lower() == 'nan':
                author = ''
            
            # Make sure we have a title
            if title and title.lower() != 'nan':
                tasks_to_run.append(process_book(context, scraper, df, idx, title, author, semaphore))
        
        await asyncio.gather(*tasks_to_run)
        await browser.close()
        
    print("--- Rebuilding Excel File with new data ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from format_madwoman import format_madwoman
        format_madwoman(EXCEL_FILE, EXCEL_FILE)
        
        # Copy to Downloads aggressively
        os.system(r'powershell -Command "Copy-Item e:\Internship\PocketFM\madeleine_milburn_combined.xlsx -Destination C:\Users\noelr\Downloads\madeleine_milburn_combined.xlsx -Force"')
    except Exception as e:
        print(f"[Warning] Could not reapply style or copy: {e}")
        
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
