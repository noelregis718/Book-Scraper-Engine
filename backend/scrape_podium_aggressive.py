import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

file_lock = asyncio.Lock()

async def safe_save(df, excel_path):
    async with file_lock:
        try:
            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"Error saving excel: {e}", flush=True)

async def process_book(index, row, df, excel_path, scraper, context, semaphore):
    title = str(row.get("Book Title", "")).strip()
    author = str(row.get("Author", "")).strip()
    if author.lower() == 'nan': author = ""
    if title.lower() == 'nan' or not title: return

    # Skip if we already have the rating (indicating it was scraped)
    rating = str(row.get("Book 1 Rating", ""))
    if rating and rating.lower() != "nan" and rating.strip() != "" and rating.strip() != "Not Found":
        return

    async with semaphore:
        print(f"[{index}] Scraping Goodreads data for: '{title}' by '{author}'", flush=True)
        data = await scraper.scrape_goodreads_data(context, title, author)
        
        if data:
            df.at[index, "Goodreads Series URL"] = data.get("GoodReads_Series_URL", "")
            df.at[index, "Book 1 Rating"] = data.get("Book1_Rating", "")
            df.at[index, "Number of Book 1 Ratings"] = data.get("Book1_Num_Ratings", "")
            df.at[index, "Number of Primary Books"] = data.get("Num_Primary_Books", "")
            
            pages = data.get("Num_Pages", "")
            df.at[index, "Number of Pages in Book 1"] = pages

            # For Subgenre, we can combine Goodreads top tags
            subgenre = data.get("Sub_Genre", "")
            main_genre = data.get("Genre", "")
            combined_sub = f"{main_genre}, {subgenre}".strip(", ")
            if combined_sub and combined_sub != "N/A" and combined_sub != "N/A, N/A":
                df.at[index, "Subgenre"] = combined_sub
                
            print(f"[{index}] Successfully scraped Goodreads for: '{title}'", flush=True)
            await safe_save(df, excel_path)
        else:
            print(f"[{index}] No Goodreads data found for '{title}'", flush=True)
            # Mark as attempted so we don't retry endlessly
            df.at[index, "Book 1 Rating"] = "Not Found"
            await safe_save(df, excel_path)

async def run_aggressive_scraper(excel_path):
    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found.")
        return

    df = pd.read_excel(excel_path)
    
    # Ensure columns exist
    cols = ["Goodreads Series URL", "Book 1 Rating", "Number of Book 1 Ratings", 
            "Number of Primary Books", "Number of Pages in Book 1", "Subgenre", "Tier Mapping"]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
            
    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(5)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        logged_in = await scraper.login_to_goodreads(page)
        if not logged_in:
            print("Failed to log in. Proceeding anyway.")
            
        tasks = []
        for index, row in df.iterrows():
            tasks.append(process_book(index, row, df, excel_path, scraper, context, semaphore))
            
        await asyncio.gather(*tasks)
        await browser.close()
        
    print("Applying styling...")
    os.system(f"python {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style_excel.py')}")
    print("Done!")

if __name__ == "__main__":
    excel = r"e:\Internship\PocketFM\podium_data.xlsx"
    asyncio.run(run_aggressive_scraper(excel))
