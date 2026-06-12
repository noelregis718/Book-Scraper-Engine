import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

try:
    from classify_perez import classify_subgenre
except ImportError:
    # Fallback if classify_perez doesn't exist
    def classify_subgenre(text):
        if 'romance' in text.lower() or 'fantasy' in text.lower():
            return "Fantasy Romance"
        return None

EXCEL_FILE = r"e:\Internship\PocketFM\del_rey_romantasy_books.xlsx"
MAX_CONCURRENT = 10
MAX_ROWS = 5000

async def process_row(context, scraper, idx, title, author, df, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        
        try:
            print(f"[{idx}] Searching: '{safe_title}' by {safe_author}...")
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
                
                print(f"[{idx}] Done. Romantasy: {df.at[idx, 'Romantasy = Yes or No?']} ({df.at[idx, 'Romantasy Sub-Genre of series']})")
            else:
                print(f"[{idx}] Not Found.")
                
        except Exception as e:
            print(f"[{idx}] Error scraping '{safe_title}': {e}")

async def run_aggressive_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
    
    # Initialize empty columns if they don't exist
    for col in ["GoodReads series link", "Number of PRIMARY books in the series", 
                "Rating (out of 5) of Primary Book 1", "Ratings (#) of Primary Book 1", 
                "Synopsis (if available)", "Romantasy = Yes or No?", "Romantasy Sub-Genre of series"]:
        if col not in df.columns:
            df[col] = ""
            
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
        await login_page.close()
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        print("--- Scanning for books missing a Synopsis or Link ---")
        for idx in range(min(MAX_ROWS, len(df))):
            title = str(df.at[idx, 'Name of Series']).strip()
            author = str(df.at[idx, 'Author Name']).strip()
            synopsis = str(df.at[idx, 'Synopsis (if available)']).strip()
            link = str(df.at[idx, 'GoodReads series link']).strip()
            
            if not title or title.lower() == 'nan':
                continue
                
            if not synopsis or synopsis == 'N/A' or synopsis.lower() == 'nan' or not link or link == 'N/A' or link.lower() == 'nan':
                tasks.append(process_row(context, scraper, idx, title, author, df, semaphore))
                
        print(f"Queued {len(tasks)} books for aggressive scraping.")
        
        if tasks:
            await asyncio.gather(*tasks)
            
        await browser.close()
        
    print("--- Saving Excel ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    print("Opening Excel file...")
    try:
        os.startfile(EXCEL_FILE)
    except Exception as e:
        print(f"Could not open file: {e}")
        
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_aggressive_scrape())
