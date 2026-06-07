import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\deborah_harris_merged.xlsx"
MAX_CONCURRENT = 5

async def process_book(context, scraper, idx, title, author, df, semaphore):
    async with semaphore:
        safe_title = str(title).encode('ascii', 'ignore').decode('ascii')
        safe_author = str(author).encode('ascii', 'ignore').decode('ascii')
        print(f"[{idx}] Scraping metadata for '{safe_title}' by {safe_author}...")
        
        try:
            # We don't have an existing URL, so it will search by title + author
            data = await scraper.scrape_goodreads_data(context, title, author)
            
            if data:
                s_link = data.get('GoodReads_Series_URL')
                if not s_link or s_link == 'N/A':
                    s_link = data.get('GoodReads_Book_URL', 'N/A')
                if s_link == 'N/A': s_link = ''
                df.at[idx, 'GoodReads series link'] = s_link
                
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                
                rating = data.get('Book1_Rating', 'N/A')
                if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = rating
                
                count = data.get('Book1_Num_Ratings', 'N/A')
                if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                df.at[idx, 'Ratings (#) of Primary Book 1'] = count
                
                df.at[idx, 'Synopsis (if available)'] = data.get('Description', 'N/A')
                
                print(f"[{idx}] Success: Extracted data for '{safe_title}'.")
            else:
                print(f"[{idx}] Failed to find details for '{safe_title}'.")
                
        except Exception as e:
            print(f"[{idx}] Error scraping '{safe_title}': {e}")


async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
            
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna("").astype(str)

    tasks = []
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        for idx in range(len(df)):
            title = str(df.at[idx, 'Name of Series']).strip()
            author = str(df.at[idx, 'Author Name']).strip()
            
            # Skip if title is empty
            if not title or title.lower() == 'nan':
                continue
                
            # If already scraped (synopsis exists), we could skip, but user said "all"
            synopsis = str(df.at[idx, 'Synopsis (if available)']).strip()
            if synopsis and synopsis.lower() != 'nan' and synopsis != 'N/A':
                print(f"[{idx}] Skipping '{title}', synopsis already exists.")
                continue

            tasks.append(process_book(context, scraper, idx, title, author, df, semaphore))
            
        print(f"Starting {len(tasks)} book scrape tasks concurrently...")
        await asyncio.gather(*tasks)
        
        await login_page.close()
        await browser.close()
        
    print("--- Saving Excel ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from style_books_authors import apply_styling
        apply_styling(EXCEL_FILE)
    except Exception as e:
        print(f"Could not apply styling: {e}")
        import subprocess
        subprocess.Popen(["start", EXCEL_FILE], shell=True)
        
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
