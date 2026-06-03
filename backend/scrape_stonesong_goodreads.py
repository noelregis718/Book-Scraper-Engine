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

    # Only update Author if it's missing or empty
    existing_author = str(df.at[idx, "Author Name"]).strip()
    scraped_author = data.get("Author_Found", "")
    if (not existing_author or existing_author.lower() == 'nan' or existing_author == '[Author name to be fetched]') and scraped_author and scraped_author != "N/A":
        df.at[idx, "Author Name"] = scraped_author

    df.at[idx, "GoodReads series link"]                 = link
    df.at[idx, "Number of PRIMARY books in the series"] = data.get("Num_Primary_Books", "1")
    df.at[idx, "Rating (out of 5) of Primary Book 1"]   = data.get("Book1_Rating",      data.get("GoodReads_Rating", "N/A"))
    df.at[idx, "Ratings (#) of Primary Book 1"]         = data.get("Book1_Num_Ratings", data.get("GoodReads_Rating_Count", "N/A"))
    df.at[idx, "Synopsis (if available)"]               = data.get("Description", "N/A")
    df.at[idx, "Romantasy = Yes or No?"]                = data.get("Romantasy_Subgenre", "No")
    df.at[idx, "Romantasy Sub-Genre of series"]         = data.get("Genre", "N/A")

async def process_row(context, scraper, df, idx, semaphore, excel_path, file_lock):
    async with semaphore:
        title  = str(df.at[idx, "Name of Series"]).strip()
        author = str(df.at[idx, "Author Name"]).strip()
        
        if author.lower() == 'nan' or author == '[Author name to be fetched]': author = ""

        if title.lower() in ["", "nan"]:
            return

        print(f"  [Searching] '{title}' by {author if author else '[Unknown Author]'}")

        try:
            # Scrape Goodreads data
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                save_book_data(df, idx, data)
                link = df.at[idx, "GoodReads series link"]
                rating = df.at[idx, "Rating (out of 5) of Primary Book 1"]
                new_auth = df.at[idx, "Author Name"]
                print(f"  [OK] '{title}' by {new_auth} -> {link} | Rating: {rating}")
            else:
                df.at[idx, "GoodReads series link"] = "N/A"
                print(f"  [Not Found] '{title}'")
        except Exception as e:
            print(f"  [Error] '{title}': {e}")
            df.at[idx, "GoodReads series link"] = "N/A"

        async with file_lock:
            try:
                df.to_excel(excel_path, index=False)
            except Exception as save_err:
                print(f"  [Save Error] {save_err}")

async def scrape_stonesong(excel_path, limit=500):
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

        current_link = str(row.get("GoodReads series link", "")).strip()
        if current_link and current_link.lower() not in ["", "nan", "n/a"]:
            continue

        rows_to_process.append(idx)
        if len(rows_to_process) >= limit:
            break

    print(f"Books to scrape: {len(rows_to_process)}\n")

    if not rows_to_process:
        print("Nothing to scrape.")
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
        print("[System] Login done. Starting scrape...\n")

        tasks = [
            process_row(context, scraper, df, idx, semaphore, excel_path, file_lock)
            for idx in rows_to_process
        ]
        await asyncio.gather(*tasks)

        print("\nAll scraping complete!")
        try:
            await browser.close()
        except Exception:
            pass

if __name__ == "__main__":
    base       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base, "Stonesong_Audited_Master_Catalog.xlsx")
    asyncio.run(scrape_stonesong(excel_path, limit=500))
