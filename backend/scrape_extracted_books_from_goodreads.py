import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\extracted_book_titles_authors.xlsx"
MAX_CONCURRENT = 10

async def process_book(scraper, context, idx, title, author, df):
    print(f"  [Scraping] Opening '{title}'...")
    
    details = await scraper.scrape_goodreads_data(
        context=context,
        title=title,
        author=author
    )
    
    if details:
        # If author was missing, update it with Goodreads's author
        if not author and details.get('Author_Found', '') != 'Unknown':
            df.at[idx, 'Author Name'] = details.get('Author_Found')
        
        df.at[idx, 'GoodReads series link'] = details.get('GoodReads_Series_URL', '')
        df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details.get('Book1_Rating', '')
        df.at[idx, 'Ratings (#) of Primary Book 1'] = details.get('Book1_Num_Ratings', '')
        df.at[idx, 'Number of PRIMARY books in the series'] = details.get('Num_Primary_Books', '')
        df.at[idx, 'Synopsis (if available)'] = details.get('Description', '')
        
        genres = [g for g in [details.get('Genre', ''), details.get('Sub_Genre', '')] if g and g != 'N/A']
        df.at[idx, 'Romantasy Sub-Genre of series'] = ", ".join(genres)
        df.at[idx, 'Romantasy = Yes or No?'] = "No" 
        
        print(f"  [Success] Scraped details for '{title}'")
    else:
        print(f"  [Failed] Could not find details for '{title}'")

async def main():
    df = pd.read_excel(EXCEL_FILE)
    scraper = GoodreadsScraper()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Determine all rows that need scraping
        tasks_to_process = []
        for idx, row in df.iterrows():
            title = str(row.get('Name of Series', '')).strip()
            author = str(row.get('Author Name', '')).strip()
            synopsis = str(row.get('Synopsis (if available)', '')).strip()
            
            if title.lower() == 'nan' or not title:
                continue
                
            if synopsis and synopsis.lower() != 'nan':
                continue
                
            if author.lower() == 'nan':
                author = ""
                
            tasks_to_process.append((idx, title, author))
            
        print(f"\nFound {len(tasks_to_process)} books to scrape.")
        
        # Chunk the tasks into groups of MAX_CONCURRENT (10)
        for i in range(0, len(tasks_to_process), MAX_CONCURRENT):
            chunk = tasks_to_process[i:i + MAX_CONCURRENT]
            print(f"\n==========================================")
            print(f"Processing chunk {i//MAX_CONCURRENT + 1} ({len(chunk)} books) concurrently...")
            print(f"==========================================")
            
            coroutines = []
            for idx, title, author in chunk:
                coroutines.append(process_book(scraper, context, idx, title, author, df))
                
            await asyncio.gather(*coroutines)
            
            print(f"  [Saved] Saving progress to Excel...")
            df.to_excel(EXCEL_FILE, index=False)
            
        print("\nALL BOOKS PROCESSED!")
        df.to_excel(EXCEL_FILE, index=False)
        
        try:
            from apply_jra_style import apply_styling
            apply_styling(EXCEL_FILE)
            print("--- Applied final styling ---")
        except Exception as e:
            print(f"Could not apply final styling: {e}")
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
