import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from apply_jra_style import apply_styling

try:
    from classify_perez import classify_subgenre
except ImportError:
    try:
        from classify_root_literary import classify_subgenre
    except ImportError:
        def classify_subgenre(text): return ""

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'New_Agency.xlsx')
MAX_CONCURRENT = 3 # lowered slightly for stability

excel_lock = asyncio.Lock()

async def process_row(context, scraper, idx, title, author, df, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        
        try:
            print(f"[{idx+2}] Aggressively Searching: '{safe_title}' by {safe_author}...", flush=True)
            data = await scraper.scrape_goodreads_data(context, title, author)
            
            if data:
                link = data.get('GoodReads_Series_URL')
                if not link or link == 'N/A':
                    link = data.get('GoodReads_Book_URL', 'N/A')
                if link == 'N/A': link = ''
                    
                df.at[idx, 'GoodReads series link'] = link
                df.at[idx, 'Number of PRIMARY books in the series'] = str(data.get('Num_Primary_Books', '1'))
                
                rating = str(data.get('Book1_Rating', 'N/A'))
                if rating == 'N/A': rating = str(data.get('GoodReads_Rating', 'N/A'))
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = rating
                
                count = str(data.get('Book1_Num_Ratings', 'N/A'))
                if count == 'N/A': count = str(data.get('GoodReads_Rating_Count', 'N/A'))
                df.at[idx, 'Ratings (#) of Primary Book 1'] = count
                
                synopsis = str(data.get('Description', 'N/A'))
                df.at[idx, 'Synopsis (if available)'] = synopsis
                
                publisher = data.get('Publisher', 'N/A')
                if publisher != 'N/A':
                    df.at[idx, 'Publisher'] = publisher
                
                combined_text = str(synopsis) + " " + str(title)
                subgenre = classify_subgenre(combined_text)
                
                if subgenre:
                    df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
                    df.at[idx, 'Romantasy Sub-Genre of series'] = subgenre
                else:
                    df.at[idx, 'Romantasy = Yes or No?'] = "No"
                    df.at[idx, 'Romantasy Sub-Genre of series'] = ""
                
                print(f"[{idx+2}] Successfully scraped '{safe_title}'. Romantasy: {df.at[idx, 'Romantasy = Yes or No?']}", flush=True)
            else:
                print(f"[{idx+2}] Not Found '{safe_title}'.", flush=True)
                
            # Safely write to excel one by one
            async with excel_lock:
                df.to_excel(EXCEL_FILE, index=False)
                try:
                    apply_styling(EXCEL_FILE)
                except Exception:
                    pass
                print(f"  [Auto-Save] Progress saved after '{safe_title}'.", flush=True)
                
        except Exception as e:
            print(f"[{idx+2}] Error scraping '{safe_title}': {e}", flush=True)

async def run_aggressive_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading Excel file: {EXCEL_FILE}", flush=True)
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
        print("Logging in to Goodreads...", flush=True)
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        # Row 24 in Excel corresponds to index 22 in pandas (since header is row 1, index 0 is row 2)
        START_IDX = 22
        
        print(f"--- Queuing books from row {START_IDX+2} to {len(df)+1} for aggressive scraping ---", flush=True)
        for idx in range(START_IDX, len(df)):
            title = str(df.at[idx, 'Name of Series']).strip()
            author = str(df.at[idx, 'Author Name']).strip()
            synopsis = str(df.at[idx, 'Synopsis (if available)']).strip()
            link = str(df.at[idx, 'GoodReads series link']).strip()
            
            if not title or title.lower() == 'nan':
                continue
                
            if not synopsis or synopsis == 'N/A' or synopsis.lower() == 'nan' or not link or link == 'N/A' or link.lower() == 'nan':
                tasks.append(process_row(context, scraper, idx, title, author, df, semaphore))
                
        print(f"Queued {len(tasks)} books for aggressive scraping.", flush=True)
        
        if tasks:
            await asyncio.gather(*tasks)
            
        await browser.close()
        
    print("ALL DONE!", flush=True)

if __name__ == '__main__':
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    asyncio.run(run_aggressive_scrape())
