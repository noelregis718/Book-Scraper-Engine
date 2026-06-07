import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\books_authors.xlsx"
MAX_CONCURRENT = 5

async def process_book(context, scraper, idx, title, author, df, semaphore):
    async with semaphore:
        safe_title = str(title).encode('ascii', 'ignore').decode('ascii')
        print(f"[{idx}] Re-scraping genres for '{safe_title}'...")
        try:
            existing_url = str(df.at[idx, 'GoodReads series link'])
            if existing_url.lower() == 'nan' or not existing_url.startswith('http'):
                existing_url = "N/A"

            data = await scraper.scrape_goodreads_data(context, title, author, existing_url=existing_url)
            if data:
                g1 = str(data.get('Genre', '')).lower()
                g2 = str(data.get('Sub_Genre', '')).lower()
                rom_sub = str(data.get('Romantasy_Subgenre', '')).lower()
                
                # Determine if it's Romantasy based on actual Goodreads genres
                is_romantasy = False
                if rom_sub == 'yes':
                    is_romantasy = True
                elif ('romance' in g1 or 'romance' in g2) and ('fantasy' in g1 or 'fantasy' in g2 or 'magic' in g1 or 'magic' in g2 or 'paranormal' in g1 or 'paranormal' in g2):
                    is_romantasy = True
                elif 'romantasy' in g1 or 'romantasy' in g2:
                    is_romantasy = True

                synopsis = str(df.at[idx, 'Synopsis (if available)'])
                
                # Map subgenre
                sub = identify_subgenre(synopsis, [g1, g2])
                
                # If we know it's romantasy but taxonomy didn't pick up a sub-genre, we can try to force a generic one or keep N/A but mark Yes
                if is_romantasy:
                    df.at[idx, 'Romantasy = Yes or No?'] = 'Yes'
                    # Default fallback if taxonomy fails
                    if sub == 'N/A':
                        if 'urban' in g1 or 'urban' in g2: sub = "Urban / Contemporary Fantasy Romance"
                        elif 'paranormal' in g1 or 'paranormal' in g2: sub = "Paranormal Romance"
                        elif 'high' in g1 or 'high' in g2: sub = "High Fantasy Court Adventure"
                        else: sub = "High Fantasy Court Adventure" # Most common default for romantasy
                    df.at[idx, 'Romantasy Sub-Genre of series'] = sub
                else:
                    # Not romantasy according to Goodreads genres
                    # But wait, if ai classifier previously picked it up, trust it
                    prev_yes = str(df.at[idx, 'Romantasy = Yes or No?']).strip().lower() == 'yes'
                    if prev_yes or sub != 'N/A':
                        df.at[idx, 'Romantasy = Yes or No?'] = 'Yes'
                        if sub == 'N/A': sub = "High Fantasy Court Adventure"
                        df.at[idx, 'Romantasy Sub-Genre of series'] = sub
                    else:
                        df.at[idx, 'Romantasy = Yes or No?'] = 'No'
                        df.at[idx, 'Romantasy Sub-Genre of series'] = 'N/A'
                
                print(f"[{idx}] Done. Romantasy: {df.at[idx, 'Romantasy = Yes or No?']} | Sub: {df.at[idx, 'Romantasy Sub-Genre of series']}")
            else:
                print(f"[{idx}] Details not found for '{safe_title}'.")
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
            
            if not title or title.lower() == 'nan':
                continue
                
            tasks.append(process_book(context, scraper, idx, title, author, df, semaphore))
            
        print(f"Starting {len(tasks)} genre scrape tasks concurrently...")
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
