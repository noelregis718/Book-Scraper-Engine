import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\New_Romantasy_Books.xlsx"

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        scraper = GoodreadsScraper(headless=False)
        
        for idx, row in df.iterrows():
            title = str(row.get('Name of Series', '')).strip()
            author = str(row.get('Author Name', '')).strip()
            existing_link = str(row.get('GoodReads series link', '')).strip()
            
            if not title or title.lower() == 'nan':
                continue
                
            # Skip if already enriched
            rating = str(row.get('Rating (out of 5) of Primary Book 1', '')).strip()
            if rating != 'nan' and rating and rating != 'N/A' and 'goodreads.com' in existing_link:
                print(f"Skipping {title} by {author} - already has details.")
                continue
                
            print(f"\n[{idx+1}/{len(df)}] Searching Goodreads for: {title} by {author}")
            
            try:
                details = await scraper.scrape_goodreads_data(context, title, author)
                
                if details:
                    if details.get("GoodReads_Series_URL") and details.get("GoodReads_Series_URL") != "N/A":
                        df.at[idx, 'GoodReads series link'] = details.get("GoodReads_Series_URL")
                    elif details.get("GoodReads_Book_URL") and details.get("GoodReads_Book_URL") != "N/A":
                        df.at[idx, 'GoodReads series link'] = details.get("GoodReads_Book_URL")
                        
                    if details.get("Num_Primary_Books") and details.get("Num_Primary_Books") != "N/A":
                        df.at[idx, 'Number of PRIMARY books in the series'] = details.get("Num_Primary_Books")
                        
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details.get("GoodReads_Rating", "")
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = details.get("GoodReads_Rating_Count", "")
                    df.at[idx, 'Synopsis (if available)'] = details.get("Description", "")
                    
                    # Save incrementally to not lose data on crash
                    df.to_excel(EXCEL_FILE, index=False)
            except Exception as e:
                print(f"Error scraping {title}: {e}")
                
            # Small delay to avoid rate limits
            await asyncio.sleep(2)
            
        await browser.close()
        
    os.system("python format_new_romantasy.py")
    print(f"\nAll books enriched! Saved and formatted {EXCEL_FILE}.")

if __name__ == "__main__":
    asyncio.run(main())
