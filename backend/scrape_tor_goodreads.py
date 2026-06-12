import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

# Configuration
CATALOG_FILE = r"e:\Internship\PocketFM\agency_template.xlsx"
BATCH_SIZE = 10
HEADLESS = False

async def process_book(index, row, context, gr_scraper):
    author_name = str(row['Author Name']).strip()
    book_title = str(row['Name of Series']).strip()
    print(f"  [Scraping] Row #{index+2} (Excel): {book_title} by {author_name}...", flush=True)
    
    try:
        gr_data = await gr_scraper.scrape_goodreads_data(context, book_title, author_name)
        return index, gr_data
    except Exception as e:
        print(f"    [Error] Row {index+2}: {e}")
        return index, None

async def main():
    if not os.path.exists(CATALOG_FILE):
        print(f"File {CATALOG_FILE} not found!")
        return

    df = pd.read_excel(CATALOG_FILE)
    
    # Check if we need to initialize columns if they don't exist
    cols_to_add = [
        'GoodReads series link', 'Number of PRIMARY books in the series',
        'Rating (out of 5) of Primary Book 1', 'Ratings (#) of Primary Book 1',
        'Synopsis (if available)', 'Romantasy = Yes or No?', 'Romantasy Sub-Genre of series'
    ]
    for col in cols_to_add:
        if col not in df.columns:
            df[col] = pd.NA
            
    # Identify rows missing GoodReads series link
    mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A') | (df['GoodReads series link'] == '')
    df_missing = df[mask]
    
    if df_missing.empty:
        print("No missing URLs found! The catalog is complete.")
        return

    print(f"Found {len(df_missing)} books missing Goodreads data. Starting Scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context()
        
        gr_scraper = GoodreadsScraper(headless=HEADLESS)
        
        # Mandatory Login
        print("[System] Performing Mandatory Login...")
        login_page = await context.new_page()
        login_success = await gr_scraper.login_to_goodreads(login_page)
        await login_page.close()
        
        if not login_success:
            print("[Error] Login failed! Aborting scraping.")
            await browser.close()
            return

        missing_indices = df_missing.index.tolist()
        for i in range(0, len(missing_indices), BATCH_SIZE):
            batch_indices = missing_indices[i:i+BATCH_SIZE]
            print(f"\n>>> Starting Batch {(i//BATCH_SIZE) + 1}...")
            
            tasks = []
            for idx in batch_indices:
                row = df.loc[idx]
                tasks.append(process_book(idx, row, context, gr_scraper))
            
            batch_results = await asyncio.gather(*tasks)
            
            for idx, gr_data in batch_results:
                if gr_data:
                    url = gr_data.get('GoodReads_Series_URL')
                    if not url or url == "N/A":
                        url = gr_data.get('GoodReads_Book_URL', 'N/A')
                        
                    df.at[idx, 'GoodReads series link'] = url
                    df.at[idx, 'Number of PRIMARY books in the series'] = gr_data.get('Num_Primary_Books', 'N/A')
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = gr_data.get('Book1_Rating', 'N/A')
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = gr_data.get('Book1_Num_Ratings', 'N/A')
                    df.at[idx, 'Synopsis (if available)'] = gr_data.get('Description', 'N/A')
                    df.at[idx, 'Romantasy = Yes or No?'] = gr_data.get('Romantasy_Subgenre', 'N/A')
                    
                    genre = gr_data.get('Genre', 'N/A')
                    subgenre = gr_data.get('Sub_Genre', 'N/A')
                    combined_genre = f"{genre}, {subgenre}" if subgenre != 'N/A' else genre
                    df.at[idx, 'Romantasy Sub-Genre of series'] = combined_genre
            
            df.to_excel(CATALOG_FILE, index=False)
            print("Batch Saved. Catalog updated.")
            
        print(f"\nScraping Complete! Final file updated: {CATALOG_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
