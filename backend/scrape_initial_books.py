import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from apply_jra_style import apply_styling

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'New_Agency.xlsx')
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    
    # Process the first 17 rows (from the initial images)
    num_to_process = 17
    
    scraper = GoodreadsScraper(headless=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        await scraper.login_to_goodreads(page)
        
        for idx in range(min(num_to_process, len(df))):
            row = df.iloc[idx]
            title = str(row.get('Name of Series', '')).strip()
            author = str(row.get('Author Name', '')).strip()
            
            # Skip if title/author is empty
            if not title or title.lower() in ['nan', 'none', '']:
                continue
                
            # Skip if we already have the rating
            existing_rating = str(row.get('Rating (out of 5) of Primary Book 1', '')).strip()
            if existing_rating and existing_rating.lower() not in ['nan', 'none', '', 'n/a']:
                print(f"[{idx+1}/{num_to_process}] Skipping '{title}' by {author} - already scraped.")
                continue
                
            print(f"[{idx+1}/{num_to_process}] Scraping details for '{title}' by {author}...")
            
            try:
                data = await scraper.scrape_goodreads_data(context, title=title, author=author, existing_url=None)
                
                if data:
                    # Update columns if data is found
                    df.at[idx, 'Publisher'] = data.get("Publisher", df.at[idx, 'Publisher'])
                    df.at[idx, 'GoodReads series link'] = data.get("GoodReads_Book_URL", df.at[idx, 'GoodReads series link'])
                    df.at[idx, 'Number of PRIMARY books in the series'] = data.get("Num_Primary_Books", df.at[idx, 'Number of PRIMARY books in the series'])
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = data.get("Book1_Rating", df.at[idx, 'Rating (out of 5) of Primary Book 1'])
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = data.get("Book1_Num_Ratings", df.at[idx, 'Ratings (#) of Primary Book 1'])
                    df.at[idx, 'Synopsis (if available)'] = data.get("Description", df.at[idx, 'Synopsis (if available)'])
                    df.at[idx, 'Romantasy Sub-Genre of series'] = data.get("Romantasy_Subgenre", df.at[idx, 'Romantasy Sub-Genre of series'])
                    print(f"  [Success] Updated '{title}'")
                    
                    # Auto-save after each successful scrape
                    df.to_excel(excel_path, index=False)
                    try:
                        apply_styling(excel_path)
                    except Exception as e:
                        print(f"Error styling: {e}")
                else:
                    print(f"  [Failed] Could not extract details for '{title}'")
                    
            except Exception as e:
                print(f"  [Error] Processing '{title}': {e}")
                
        # Final save
        df.to_excel(excel_path, index=False)
        try:
            apply_styling(excel_path)
        except Exception:
            pass
        print("\n--- Scrape Complete! ---")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
