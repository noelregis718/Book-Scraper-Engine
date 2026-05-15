import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os
import json
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

# Configuration
CATALOG_FILE = "Bookends_Literary_Catalog_Final.xlsx"
CONCURRENCY_LIMIT = 10 # 10 tabs at once

async def process_book(context, scraper, df, idx, semaphore):
    async with semaphore:
        # Map to the specific 11-column headers
        series_name = str(df.at[idx, 'Name of Series'])
        author_name = str(df.at[idx, 'Author Name'])
        
        print(f"  [Tab Start] {series_name} by {author_name}...")
        
        try:
            # Aggressive Search & Link Capture
            data = await scraper.scrape_goodreads_data(context, series_name, author_name)
            
            if data:
                # AGGRESSIVE LINK SAVING: Force capture the browser URL if series link is N/A
                link = data.get('GoodReads_Series_URL')
                if not link or link == "N/A":
                    link = data.get('GoodReads_Book_URL')
                
                df.at[idx, 'GoodReads series link'] = link
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', '1')
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = data.get('GoodReads_Rating', 'N/A')
                df.at[idx, 'Ratings (#) of Primary Book 1'] = data.get('GoodReads_Rating_Count', 'N/A')
                df.at[idx, 'Synopsis (if available)'] = data.get('Description', 'N/A')
                
                # AI Classification
                genre = data.get('Genre', 'N/A')
                subgenre = identify_subgenre(df.at[idx, 'Synopsis (if available)'], [genre])
                
                if subgenre != "N/A":
                    df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
                    df.at[idx, 'Romantasy Sub-Genre of series'] = subgenre
                else:
                    if 'Romance' in genre and ('Fantasy' in genre or 'Paranormal' in genre):
                        df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
                        df.at[idx, 'Romantasy Sub-Genre of series'] = "Urban / Contemporary Fantasy Romance"
                    else:
                        df.at[idx, 'Romantasy = Yes or No?'] = "No"
                        df.at[idx, 'Romantasy Sub-Genre of series'] = "N/A"
                        
                print(f"    [Success] {series_name} -> Link Saved.")
            else:
                print(f"    [Skip] No data found for {series_name}")
                df.at[idx, 'GoodReads series link'] = None # Blank as requested
                
        except Exception as e:
            print(f"    [Error] {series_name}: {e}")

async def enrich_bookends():
    if not os.path.exists(CATALOG_FILE):
        print(f"Error: {CATALOG_FILE} not found!")
        return

    # Load data
    df = pd.read_excel(CATALOG_FILE)
    
    # Identify rows needing enrichment
    mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A')
    rows_to_process = df[mask].index.tolist()[:20] # LIMIT TO NEXT 20
    
    print(f"Total entries in Bookends Catalog: {len(df)}")
    print(f"Remaining to search: {len(rows_to_process)}")

    if not rows_to_process:
        print("Everything is already enriched!")
        return

    async with async_playwright() as p:
        # Visible mode for login check
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        # 1. Mandatory Login (Visible)
        print("[System] Performing Mandatory Login for Bookends Mission...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        print("[System] Login Complete. Closing login tab.")
        await login_page.close()

        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        
        # Process in batches of 10
        for i in range(0, len(rows_to_process), CONCURRENCY_LIMIT):
            batch_indices = rows_to_process[i:i+CONCURRENCY_LIMIT]
            print(f"\n>>> Launching Bookends 10-Tab Batch {(i//CONCURRENCY_LIMIT)+1}...")
            
            tasks = [process_book(context, scraper, df, idx, semaphore) for idx in batch_indices]
            await asyncio.gather(*tasks)
            
            # Save progress after each batch
            df.to_excel(CATALOG_FILE, index=False)
            print(f"Batch saved to {CATALOG_FILE}.")

        await browser.close()
        print("\nBookends Enrichment Mission Complete!")
        # Auto-open the final file
        os.startfile(CATALOG_FILE)

if __name__ == "__main__":
    asyncio.run(enrich_bookends())
