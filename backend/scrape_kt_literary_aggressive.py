import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\KT_Literary_Merged_Formatted.xlsx"
MAX_ROWS = 100  # More than 64
MAX_CONCURRENT = 5

async def process_row(context, scraper, idx, title, author, df, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        
        try:
            print(f"[{idx}] Searching: '{safe_title}' by {safe_author}...")
            # Get existing link from dataframe
            existing_link = str(df.at[idx, 'GoodReads series link']).strip()
            existing = existing_link if (existing_link and existing_link != 'N/A' and existing_link.lower() != 'nan') else "N/A"
            data = await scraper.scrape_goodreads_data(context, title, author, existing_url=existing)
            
            if data:
                link = data.get('GoodReads_Series_URL')
                if not link or link == "N/A":
                    link = data.get('GoodReads_Book_URL')
                
                # Use primary book rating if available, else use book rating
                rating = data.get('Book1_Rating')
                if not rating or rating == "N/A":
                    rating = data.get('GoodReads_Rating')
                    
                count = data.get('Book1_Num_Ratings')
                if not count or count == "N/A":
                    count = data.get('GoodReads_Rating_Count')
                    
                synopsis = data.get('Description')
                is_romantasy = data.get('Romantasy_Subgenre', 'No')
                sub_genre = data.get('Sub_Genre', '')
                
                # We always update the data if found
                df.at[idx, 'GoodReads series link'] = link if link else "N/A"
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = rating if rating else "N/A"
                df.at[idx, 'Ratings (#) of Primary Book 1'] = count if count else "N/A"
                df.at[idx, 'Synopsis (if available)'] = synopsis if synopsis else "N/A"
                df.at[idx, 'Romantasy = Yes or No?'] = is_romantasy
                df.at[idx, 'Romantasy Sub-Genre of series'] = sub_genre
                
                print(f"[{idx}] Done. Romantasy: {is_romantasy} ({link})")
            else:
                print(f"[{idx}] Not Found.")
                
        except Exception as e:
            print(f"[{idx}] Error scraping '{safe_title}': {e}")

async def run_scraper():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
            
    scraper = GoodreadsScraper()
    tasks = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        for idx in range(len(df)):
            title = str(df.at[idx, 'Name of Series']).strip()
            author = str(df.at[idx, 'Author Name']).strip()
            synopsis = str(df.at[idx, 'Synopsis (if available)']).strip()
            link = str(df.at[idx, 'GoodReads series link']).strip()
            
            # Skip empty titles
            if title.lower() == 'nan' or not title:
                continue
                
            # Only scrape if missing critical data (or if link is N/A)
            if not synopsis or synopsis == 'N/A' or synopsis.lower() == 'nan' or not link or link == 'N/A' or link.lower() == 'nan':
                tasks.append(process_row(context, scraper, idx, title, author, df, semaphore))
            else:
                print(f"[{idx}] Skipping '{title.encode('ascii', 'ignore').decode('ascii')}', already has data.")
                
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
        
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scraper())
