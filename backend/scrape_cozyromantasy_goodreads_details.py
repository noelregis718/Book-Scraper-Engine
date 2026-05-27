import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\CozyRomantasy_Merged.xlsx"

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper()
        
        # Optional: login if needed, though search usually works without login
        # await scraper.login_to_goodreads(await context.new_page())
        
        for idx, row in df.iterrows():
            title = str(row.get('Name of Series', '')).strip()
            author = str(row.get('Author Name', '')).strip()
            existing_link = str(row.get('GoodReads series link', '')).strip()
            
            if not title or title.lower() == 'nan':
                continue
                
            # If we already have a valid link, we might skip, but let's be aggressive
            rating = str(row.get('Rating (out of 5) of Primary Book 1', '')).strip()
            if rating != 'nan' and rating and rating != 'N/A' and 'goodreads.com' in existing_link:
                print(f"Skipping {title} by {author} - already has details.")
                continue
                
            print(f"\nSearching Goodreads for: {title} by {author}")
            
            details = await scraper.scrape_goodreads_data(context, title, author)
            
            if details:
                if details.get("GoodReads_Series_URL", "N/A") != "N/A":
                    df.at[idx, 'GoodReads series link'] = details["GoodReads_Series_URL"]
                elif details.get("GoodReads_Book_URL", "N/A") != "N/A":
                    df.at[idx, 'GoodReads series link'] = details["GoodReads_Book_URL"]
                    
                if details.get("Book1_Rating", "N/A") != "N/A":
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details["Book1_Rating"]
                elif details.get("GoodReads_Rating", "N/A") != "N/A":
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details["GoodReads_Rating"]
                    
                if details.get("Book1_Num_Ratings", "N/A") != "N/A":
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = details["Book1_Num_Ratings"]
                elif details.get("GoodReads_Rating_Count", "N/A") != "N/A":
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = details["GoodReads_Rating_Count"]
                    
                if details.get("Num_Primary_Books", "1") != "N/A":
                    df.at[idx, 'Number of PRIMARY books in the series'] = details["Num_Primary_Books"]
                    
                if details.get("Description", "N/A") != "N/A":
                    # Only overwrite synopsis if it's currently missing or short
                    curr_syn = str(row.get('Synopsis (if available)', '')).strip()
                    if len(curr_syn) < 20:
                        df.at[idx, 'Synopsis (if available)'] = details["Description"]
                        
            # Save incrementally
            df.to_excel(EXCEL_FILE, index=False)
            
        await browser.close()
        
    print(f"\nPhase 1 Complete! Saving final {EXCEL_FILE}...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
    except:
        pass

if __name__ == '__main__':
    asyncio.run(main())
