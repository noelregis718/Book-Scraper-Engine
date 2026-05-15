import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

# Configuration
CATALOG_FILE = "Speilburg_Media_Catalog_Final.xlsx"
BATCH_SIZE = 10 

async def enrich_speilburg():
    if not os.path.exists(CATALOG_FILE):
        print(f"Error: {CATALOG_FILE} not found!")
        return

    # Load data
    df = pd.read_excel(CATALOG_FILE)
    
    # Identify rows that need enrichment
    mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A')
    rows_to_process = df[mask].index.tolist()
    
    print(f"Total entries in catalog: {len(df)}")
    print(f"Entries needing enrichment: {len(rows_to_process)}")

    if not rows_to_process:
        print("Everything is already enriched!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        scraper = GoodreadsScraper(headless=False)
        
        # Mandatory Login
        print("[System] Performing Mandatory Login...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()

        # Process in batches
        for i in range(0, len(rows_to_process), BATCH_SIZE):
            batch_indices = rows_to_process[i:i+BATCH_SIZE]
            print(f"\n>>> Processing Batch {(i//BATCH_SIZE)+1} ({len(batch_indices)} items)...")
            
            for idx in batch_indices:
                series_name = str(df.at[idx, 'Name of Series'])
                author_name = str(df.at[idx, 'Author Name'])
                
                print(f"  [Enriching] {series_name} by {author_name}...")
                
                try:
                    # We search using "Series/Book Name + Author Name"
                    data = await scraper.scrape_goodreads_data(context, series_name, author_name)
                    
                    if data:
                        # FORCE LINK CAPTURE: Ensure we have a link if data exists
                        link = data.get('GoodReads_Series_URL')
                        if not link or link == "N/A":
                            link = data.get('GoodReads_Book_URL')
                        
                        df.at[idx, 'GoodReads series link'] = link
                        df.at[idx, 'Number of Primary books in series'] = data.get('Num_Primary_Books', '1')
                        df.at[idx, 'Average Rating of Series'] = data.get('GoodReads_Rating', 'N/A')
                        df.at[idx, 'Ratings count of the first book of the series'] = data.get('GoodReads_Rating_Count', 'N/A')
                        
                        synopsis = data.get('Description', 'N/A')
                        df.at[idx, 'Synopsis (if available)'] = synopsis
                        
                        # Classification
                        genre = data.get('Genre', 'N/A')
                        subgenre = identify_subgenre(synopsis, [genre])
                        
                        if subgenre != "N/A":
                            df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
                            df.at[idx, 'Romantasy Sub-Genre of series'] = subgenre
                        else:
                            # Try to see if current genre has hints
                            if 'Romance' in genre and ('Fantasy' in genre or 'Paranormal' in genre):
                                df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
                                df.at[idx, 'Romantasy Sub-Genre of series'] = "Urban / Contemporary Fantasy Romance"
                            else:
                                df.at[idx, 'Romantasy = Yes or No?'] = "No"
                                df.at[idx, 'Romantasy Sub-Genre of series'] = "N/A"
                                
                        print(f"    [Success] Found data and classified as: {df.at[idx, 'Romantasy Sub-Genre of series']}")
                    else:
                        print(f"    [Skip] No data found on Goodreads for {series_name}")
                        df.at[idx, 'GoodReads series link'] = "Not Found"
                        
                except Exception as e:
                    print(f"    [Error] Failed to process {series_name}: {e}")

            # Save progress after each batch
            df.to_excel(CATALOG_FILE, index=False)
            print(f"Batch {(i//BATCH_SIZE)+1} saved to Excel.")

        await browser.close()
        print("\nSpeilburg Enrichment Mission Complete!")
        
        # Auto-open the Excel file for the user
        print(f"[System] Opening {CATALOG_FILE} for review...")
        os.startfile(CATALOG_FILE)

if __name__ == "__main__":
    asyncio.run(enrich_speilburg())
