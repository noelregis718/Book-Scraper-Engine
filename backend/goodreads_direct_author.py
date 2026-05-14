import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

# Configuration
INPUT_FILE = "give me one complete sheet which has the names of....xlsx"
OUTPUT_FILE = "SBR_Media_Catalog_Final.xlsx"
BATCH_SIZE = 10
RUN_LIMIT = 100 # Process exactly 100 items per run
HEADLESS = False

async def process_author(index, author_name, context, gr_scraper):
    print(f"  [Goodreads] Processing Author {index+1}: {author_name}...", flush=True)
    try:
        # Search for the author's top book and get metadata
        gr_data = await gr_scraper.scrape_goodreads_data(context, "", author_name)
        
        if gr_data:
            print(f"    [Success] Matched: {gr_data.get('Book_Title')}")
            return {
                'Name of Series': gr_data.get('Book_Title', 'N/A'),
                'Author Name': author_name,
                'Publisher': 'SBR Media',
                'GoodReads series link': gr_data.get('GoodReads_Series_URL', gr_data.get('GoodReads_Book_URL', 'N/A')),
                'Number of PRIMARY books in the series': gr_data.get('Num_Primary_Books', '1'),
                'Rating (out of 5) of Primary Book 1': gr_data.get('Book1_Rating', 'N/A'),
                'Ratings (#) of Primary Book 1': gr_data.get('Book1_Num_Ratings', 'N/A'),
                'Synopsis (if available)': gr_data.get('Description', 'N/A'),
                'Romantasy = Yes or No?': gr_data.get('Romantasy_Subgenre', 'No'),
                'Romantasy Sub-Genre of series': gr_data.get('Genre', 'N/A'),
                'Name of agent': 'SBR Media'
            }
        else:
            print(f"    [Not Found] No results for {author_name}")
            return None
    except Exception as e:
        print(f"    [Error] {author_name}: {e}")
        return None

async def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found!")
        return

    # Load the author list
    df = pd.read_excel(INPUT_FILE)
    
    # Strictly start after the last 100-item run
    START_INDEX = 346
    df_to_process = df.iloc[START_INDEX:START_INDEX+RUN_LIMIT]
    
    if df_to_process.empty:
        print("No new authors to process in this range!")
        return

    print(f"Starting run from Author #{START_INDEX+1} to #{START_INDEX+len(df_to_process)}")

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
            print("[Error] Login failed! Aborting mission for security.")
            await browser.close()
            return

        results = []
        
        # Process in batches
        for i in range(0, len(df_to_process), BATCH_SIZE):
            batch = df_to_process.iloc[i:i+BATCH_SIZE]
            print(f"\n>>> Starting Batch {(i//BATCH_SIZE) + 1}...")
            
            tasks = []
            for idx, row in batch.iterrows():
                author_name = str(row['Author Name'])
                tasks.append(process_author(idx, author_name, context, gr_scraper))
            
            batch_results = await asyncio.gather(*tasks)
            
            # Collect results and save immediately
            for res in batch_results:
                if res:
                    results.append(res)
            
            # Persistent Save
            if results:
                df_new = pd.DataFrame(results)
                if os.path.exists(OUTPUT_FILE):
                    df_old = pd.read_excel(OUTPUT_FILE)
                    df_final = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=['Author Name'], keep='last')
                else:
                    df_final = df_new
                
                df_final.to_excel(OUTPUT_FILE, index=False)
                print(f"Batch Saved. Total Saved in File: {len(df_final)}")
            
        print(f"\nRun Complete! Processed {RUN_LIMIT} authors. Final file updated: {OUTPUT_FILE}")
        if os.name == 'nt':
            os.startfile(OUTPUT_FILE)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
