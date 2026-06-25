import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"e:\Internship\PocketFM\LDLA_Combined.xlsx"

async def process_row(idx, row, scraper, context):
    title = str(row.get('Name of Series', '')).strip()
    author = str(row.get('Author Name', '')).strip()
    existing_link = str(row.get('GoodReads series link', '')).strip()
    
    if not title or title.lower() == 'nan':
        return idx, None
        
    rating = str(row.get('Rating (out of 5) of Primary Book 1', '')).strip()
    if rating != 'nan' and rating and rating != 'N/A' and 'goodreads.com' in existing_link:
        print(f"Skipping '{title}' by {author} - already scraped.")
        return idx, None
        
    print(f"[Book {idx+1}] Searching Goodreads for: '{title}' by {author}")
    details = await scraper.scrape_goodreads_data(context, title, author, existing_url=existing_link)
    
    return idx, details

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Pre-cast columns to object to avoid incompatible dtype warnings
    cols_to_cast = ['GoodReads series link', 'Rating (out of 5) of Primary Book 1', 
                    'Ratings (#) of Primary Book 1', 'Number of PRIMARY books in the series', 
                    'Synopsis (if available)']
    for col in cols_to_cast:
        if col in df.columns:
            df[col] = df[col].astype('object')
            
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        page = await context.new_page()
        logged_in = await scraper.login_to_goodreads(page)
        if not logged_in:
            print("Login failed or timed out. Scraping might be limited or blocked.")
        await page.close()
        
        rows = list(df.iterrows())
        chunk_size = 8
        
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i+chunk_size]
            print(f"\n--- Processing batch {i//chunk_size + 1} of {(len(rows)+chunk_size-1)//chunk_size} ---")
            
            tasks = [process_row(idx, row, scraper, context) for idx, row in chunk]
            results = await asyncio.gather(*tasks)
            
            for idx, details in results:
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
                        curr_syn = str(df.at[idx, 'Synopsis (if available)']).strip()
                        if curr_syn == 'nan' or len(curr_syn) < 20:
                            df.at[idx, 'Synopsis (if available)'] = details["Description"]
                            
            df.to_excel(EXCEL_FILE, index=False)
            
        await browser.close()
        
    print(f"\nScraping Complete! Final data saved to {EXCEL_FILE}.")
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("Final styling applied.")
    except:
        pass

if __name__ == '__main__':
    asyncio.run(main())
