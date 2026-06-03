import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

CONCURRENCY = 3

def save_book_data(df, idx, data):
    link = data.get("GoodReads_Series_URL")
    if not link or link == "N/A":
        link = data.get("GoodReads_Book_URL", "N/A")

    # Update Author if it's found
    existing_author = str(df.at[idx, "Author Name"]).strip()
    scraped_author = data.get("Author_Found", "")
    if (not existing_author or existing_author.lower() == 'nan' or existing_author == '[Author name to be fetched]' or existing_author.lower() == 'unknown') and scraped_author and scraped_author != "N/A":
        df.at[idx, "Author Name"] = scraped_author

    # Only update link if it was missing or N/A
    current_link = str(df.at[idx, "GoodReads series link"]).strip()
    if not current_link or current_link.lower() in ["", "nan", "n/a"]:
        df.at[idx, "GoodReads series link"] = link
        
    # Update other columns only if they were missing or N/A
    if str(df.at[idx, "Rating (out of 5) of Primary Book 1"]).strip() in ["", "nan", "N/A"]:
        df.at[idx, "Number of PRIMARY books in the series"] = data.get("Num_Primary_Books", "1")
        df.at[idx, "Rating (out of 5) of Primary Book 1"]   = data.get("Book1_Rating", data.get("GoodReads_Rating", "N/A"))
        df.at[idx, "Ratings (#) of Primary Book 1"]         = data.get("Book1_Num_Ratings", data.get("GoodReads_Rating_Count", "N/A"))
        df.at[idx, "Synopsis (if available)"]               = data.get("Description", "N/A")
        df.at[idx, "Romantasy = Yes or No?"]                = data.get("Romantasy_Subgenre", "No")
        df.at[idx, "Romantasy Sub-Genre of series"]         = data.get("Genre", "N/A")

async def process_row(context, scraper, df, idx, semaphore, excel_path, file_lock):
    async with semaphore:
        title  = str(df.at[idx, "Name of Series"]).strip()
        
        # Deliberately search by book title only
        author = ""

        if title.lower() in ["", "nan"]:
            return

        print(f"  [Aggressive Search] '{title}'")

        try:
            # Scrape Goodreads data - this uses Tier 1 & Tier 2 searches
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                save_book_data(df, idx, data)
                new_auth = df.at[idx, "Author Name"]
                print(f"  [OK] '{title}' -> Author Found: {new_auth}")
            else:
                print(f"  [Not Found] '{title}'")
        except Exception as e:
            print(f"  [Error] '{title}': {e}")

        async with file_lock:
            try:
                df.to_excel(excel_path, index=False)
            except Exception as save_err:
                print(f"  [Save Error] {save_err}")

async def scrape_stonesong_aggressive(excel_path, limit=500):
    print(f"Loading: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: File not found - {excel_path}")
        return

    df = pd.read_excel(excel_path, keep_default_na=False)

    for col in [
        "Author Name",
        "GoodReads series link",
        "Number of PRIMARY books in the series",
        "Rating (out of 5) of Primary Book 1",
        "Ratings (#) of Primary Book 1",
        "Synopsis (if available)",
        "Romantasy = Yes or No?",
        "Romantasy Sub-Genre of series"
    ]:
        if col in df.columns:
            df[col] = df[col].astype(object)

    rows_to_process = []
    for idx, row in df.iterrows():
        title  = str(row.get("Name of Series", "")).strip()
        if not title or title.lower() in ["", "nan"]:
            continue

        # ONLY process rows where Author is missing
        current_author = str(row.get("Author Name", "")).strip().lower()
        if current_author not in ["", "nan", "n/a", "unknown", "[author name to be fetched]"]:
            continue

        rows_to_process.append(idx)
        if len(rows_to_process) >= limit:
            break

    print(f"Books to aggressively scrape for authors: {len(rows_to_process)}\n")

    if not rows_to_process:
        print("No missing authors left!")
        return

    file_lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(CONCURRENCY)
    scraper   = GoodreadsScraper(headless=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        print("[System] Logging in to Goodreads...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        print("[System] Login done. Starting aggressive scrape...\n")

        tasks = [
            process_row(context, scraper, df, idx, semaphore, excel_path, file_lock)
            for idx in rows_to_process
        ]
        await asyncio.gather(*tasks)

        print("\nAll aggressive scraping complete!")
        try:
            await browser.close()
        except Exception:
            pass

if __name__ == "__main__":
    base       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base, "Stonesong_Books.xlsx")
    asyncio.run(scrape_stonesong_aggressive(excel_path, limit=500))
