import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from classify_perez import classify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\Triada_Merged.xlsx"
MAX_CONCURRENT = 5

async def process_book(context, scraper, idx, title, author, df, semaphore):
    async with semaphore:
        safe_title = str(title).encode('ascii', 'ignore').decode('ascii')
        print(f"[{idx}] Scraping '{safe_title}'...")
        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                link = data.get('GoodReads_Series_URL')
                if not link or link == 'N/A':
                    link = data.get('GoodReads_Book_URL', 'N/A')
                if link == 'N/A': link = ''
                    
                df.at[idx, 'GoodReads series link'] = link
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                
                rating = data.get('Book1_Rating', 'N/A')
                if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = rating
                
                count = data.get('Book1_Num_Ratings', 'N/A')
                if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                df.at[idx, 'Ratings (#) of Primary Book 1'] = count
                
                synopsis = data.get('Description', 'N/A')
                df.at[idx, 'Synopsis (if available)'] = synopsis
                
                # Classify Romantasy
                combined_text = str(synopsis) + " " + str(title)
                subgenre = classify_subgenre(combined_text)
                
                if subgenre:
                    df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
                    df.at[idx, 'Romantasy Sub-Genre of series'] = subgenre
                else:
                    df.at[idx, 'Romantasy = Yes or No?'] = "No"
                    df.at[idx, 'Romantasy Sub-Genre of series'] = ""
                
                print(f"[{idx}] Done parsing '{safe_title}'. Romantasy: {df.at[idx, 'Romantasy = Yes or No?']}")
            else:
                print(f"[{idx}] Details not found for '{safe_title}'.")
        except Exception as e:
            print(f"[{idx}] Error scraping '{safe_title}': {e}")

async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
            
    # Convert object columns to strings to avoid nan float issues
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
            
            # Skip empty titles
            if not title or title.lower() == 'nan':
                continue
                
            tasks.append(process_book(context, scraper, idx, title, author, df, semaphore))
            
        print(f"Starting {len(tasks)} scrape tasks concurrently...")
        await asyncio.gather(*tasks)
        
        await login_page.close()
        await browser.close()
        
    print("--- Saving Excel ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
