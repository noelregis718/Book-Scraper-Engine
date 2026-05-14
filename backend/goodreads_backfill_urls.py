import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

# Configuration
CATALOG_FILE = "SBR_Media_Catalog_Final.xlsx"
BATCH_SIZE = 10
HEADLESS = False

async def process_missing_author(index, row, context, gr_scraper):
    author_name = str(row['Author Name'])
    book_title = str(row['Name of Series'])
    print(f"  [Backfill] Fixing Author #{index+1}: {author_name} ({book_title})...", flush=True)
    
    try:
        # We try to search specifically for the book + author to get the exact link
        gr_data = await gr_scraper.scrape_goodreads_data(context, book_title, author_name)
        
        if gr_data and gr_data.get('GoodReads_Book_URL'):
            # Prefer Series URL, fallback to Book URL
            final_url = gr_data.get('GoodReads_Series_URL')
            if not final_url or final_url == "N/A":
                final_url = gr_data.get('GoodReads_Book_URL', 'N/A')
            
            print(f"    [Success] Found URL: {final_url}")
            return index, final_url
        else:
            print(f"    [Not Found] Still no URL for {author_name}")
            return index, None
    except Exception as e:
        print(f"    [Error] {author_name}: {e}")
        return index, None

async def main():
    if not os.path.exists(CATALOG_FILE):
        print(f"File {CATALOG_FILE} not found!")
        return

    df = pd.read_excel(CATALOG_FILE)
    
    # Identify rows missing URLs
    mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A')
    df_missing = df[mask]
    
    if df_missing.empty:
        print("No missing URLs found! The catalog is complete.")
        return

    print(f"Found {len(df_missing)} authors missing Goodreads URLs. Starting Backfill...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context()
        
        gr_scraper = GoodreadsScraper(headless=HEADLESS)
        
        # MANDATORY LOGIN
        print("[System] Performing Mandatory Login...")
        login_page = await context.new_page()
        login_success = await gr_scraper.login_to_goodreads(login_page)
        await login_page.close()
        
        if not login_success:
            print("[Error] Login failed! Aborting backfill.")
            await browser.close()
            return

        # Process in batches
        missing_indices = df_missing.index.tolist()
        for i in range(0, len(missing_indices), BATCH_SIZE):
            batch_indices = missing_indices[i:i+BATCH_SIZE]
            print(f"\n>>> Starting Backfill Batch {(i//BATCH_SIZE) + 1}...")
            
            tasks = []
            for idx in batch_indices:
                row = df.loc[idx]
                tasks.append(process_missing_author(idx, row, context, gr_scraper))
            
            batch_results = await asyncio.gather(*tasks)
            
            # Apply results to main dataframe
            for idx, url in batch_results:
                if url and url != "N/A":
                    df.at[idx, 'GoodReads series link'] = url
            
            # Save progress after each batch
            df.to_excel(CATALOG_FILE, index=False)
            print(f"Batch Saved. Catalog updated.")
            
        print(f"\nBackfill Complete! Final file updated: {CATALOG_FILE}")
        if os.name == 'nt':
            os.startfile(CATALOG_FILE)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
