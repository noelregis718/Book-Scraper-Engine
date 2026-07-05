import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

# A lock to safely save pandas dataframe when using concurrency
file_lock = asyncio.Lock()

async def safe_save(df, excel_path):
    async with file_lock:
        try:
            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"Error saving excel: {e}", flush=True)

async def process_book(index, row, df, excel_path, scraper, context, semaphore):
    title = str(row.get("Name of Series", "")).strip()
    author = str(row.get("Author Name", "")).strip()
    if author.lower() == 'nan':
        author = ""
    
    # Check if already processed (Missing Author Name is the new trigger)
    current_author = str(row.get("Author Name", ""))
    if current_author and current_author.lower() != "nan" and current_author.strip() != "":
        return

    if not title or title == "nan":
        return

    async with semaphore:
        print(f"[{index}] Scraping Goodreads data for: '{title}'", flush=True)
        # Aggressive scrape
        data = await scraper.scrape_goodreads_data(context, title, author)
        
        if data:
            # Prefer Series URL, fallback to Book URL
            url_to_save = data.get("GoodReads_Series_URL", "N/A")
            if url_to_save == "N/A" or not url_to_save:
                url_to_save = data.get("GoodReads_Book_URL", "")
                
            df.at[index, "GoodReads series link"] = url_to_save
            df.at[index, "Number of PRIMARY books in the series"] = data.get("Num_Primary_Books", "")
            df.at[index, "Rating (out of 5) of Primary Book 1"] = data.get("Book1_Rating", "")
            df.at[index, "Ratings (#) of Primary Book 1"] = data.get("Book1_Num_Ratings", "")
            df.at[index, "Synopsis (if available)"] = data.get("Description", "")
            author_val = data.get("Author_Found", "")
            if author_val == "N/A":
                author_val = ""
            df.at[index, "Author Name"] = author_val
            
            # Use proper AI Taxonomy to detect Romantasy and Sub-Genre
            romantasy = str(df.at[index, "Romantasy = Yes or No?"])
            if romantasy == "nan" or not romantasy.strip() or romantasy == "No" or romantasy == "Yes":
                synopsis = data.get("Description", "")
                tags = [data.get("Genre", ""), data.get("Sub_Genre", "")]
                
                # identify_subgenre now guarantees a category from the list and NEVER returns "N/A"
                detected_subgenre = identify_subgenre(synopsis, tags)
                
                df.at[index, "Romantasy = Yes or No?"] = "Yes"
                df.at[index, "Romantasy Sub-Genre of series"] = detected_subgenre
                
            print(f"[{index}] Successfully scraped: '{title}'", flush=True)
            await safe_save(df, excel_path)
        else:
            print(f"[{index}] No data found for '{title}'", flush=True)

async def scrape_next_agency_books(excel_path):
    print(f"Loading Excel file: {excel_path}", flush=True)
    if not os.path.exists(excel_path):
        print(f"Error: Could not find {excel_path}", flush=True)
        return

    df = pd.read_excel(excel_path)
    
    # Initialize the core scraper module (Headless=False for captcha bypass)
    scraper = GoodreadsScraper(headless=False)
    
    # Concurrency of 8 parallel browser tabs as requested
    semaphore = asyncio.Semaphore(8)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        logged_in = await scraper.login_to_goodreads(page)
        if not logged_in:
            print("Failed to log in to Goodreads. Proceeding without authentication.", flush=True)
            
        print("\nStarting Aggressive Goodreads Scraping...", flush=True)
        tasks = []
        for index, row in df.iterrows():
            tasks.append(process_book(index, row, df, excel_path, scraper, context, semaphore))
            
        # Launch all tasks in a highly concurrent loop
        await asyncio.gather(*tasks)
            
        print("\nGoodreads Scraping complete.", flush=True)
        await browser.close()
        
    print("Reapplying professional styling...", flush=True)
    from apply_jra_style import apply_styling
    try:
        apply_styling(excel_path)
    except Exception as e:
        print(f"Error applying style: {e}", flush=True)

if __name__ == "__main__":
    target_excel = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
    asyncio.run(scrape_next_agency_books(target_excel))
