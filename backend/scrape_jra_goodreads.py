import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

# A lock to safely save pandas dataframe
file_lock = asyncio.Lock()

async def safe_save(df, excel_path):
    async with file_lock:
        try:
            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"Error saving excel: {e}")

async def process_book(index, row, df, excel_path, scraper, context, semaphore):
    title = str(row.get("Name of Series", "")).strip()
    author = str(row.get("Author Name", "")).strip()
    
    # Check if already processed (we now check if the link is missing)
    current_link = str(row.get("GoodReads series link", ""))
    if current_link and current_link != "nan" and current_link.strip() != "" and current_link != "N/A":
        return

    if not title or title == "nan":
        return

    async with semaphore:
        print(f"[{index}] Scraping: '{title}' by {author}")
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
            
            romantasy = str(df.at[index, "Romantasy = Yes or No?"])
            if romantasy == "nan" or not romantasy.strip():
                df.at[index, "Romantasy = Yes or No?"] = data.get("Romantasy_Subgenre", "No")
                df.at[index, "Romantasy Sub-Genre of series"] = data.get("Sub_Genre", "")
                
            print(f"[{index}] Done: '{title}'")
            await safe_save(df, excel_path)
        else:
            print(f"[{index}] No data for '{title}'")

async def scrape_jra_bestsellers(excel_path):
    print(f"Loading Excel file: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: Could not find {excel_path}")
        return

    df = pd.read_excel(excel_path)
    
    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(10)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        logged_in = await scraper.login_to_goodreads(page)
        if not logged_in:
            print("Failed to log in to Goodreads. Proceeding without authentication.")
            
        print("\nStarting Aggressive Concurrency...")
        tasks = []
        for index, row in df.iterrows():
            tasks.append(process_book(index, row, df, excel_path, scraper, context, semaphore))
            
        # Run all tasks concurrently
        await asyncio.gather(*tasks)
            
        print("\nScraping complete.")
        await browser.close()
        
    # After scraping, reapply professional styling
    print("Reapplying professional styling...")
    from apply_jra_style import apply_styling
    try:
        apply_styling(excel_path)
    except Exception as e:
        print(f"Error applying style: {e}")

if __name__ == "__main__":
    target_excel = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "JRA_Bestsellers_Complete.xlsx")
    asyncio.run(scrape_jra_bestsellers(target_excel))
