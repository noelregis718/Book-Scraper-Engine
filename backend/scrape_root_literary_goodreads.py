"""
Root Literary GoodReads Scraper
================================
Pattern: ONE browser window, ONE shared context, tabs open inside it.
Semaphore limits to 5 concurrent tabs at a time (like Pilkington).
"""

import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from apply_jra_style import apply_styling

CONCURRENCY = 5   # 5 tabs inside one browser window

# ------------------------------------------------------------------
# Save data from the scraper result dict into the dataframe
# ------------------------------------------------------------------
def save_book_data(df, idx, data):
    link = data.get("GoodReads_Series_URL")
    if not link or link == "N/A":
        link = data.get("GoodReads_Book_URL", "N/A")

    df.at[idx, "GoodReads series link"]                 = link
    df.at[idx, "Number of PRIMARY books in the series"] = data.get("Num_Primary_Books", "1")
    df.at[idx, "Rating (out of 5) of Primary Book 1"]   = data.get("Book1_Rating",      data.get("GoodReads_Rating", "N/A"))
    df.at[idx, "Ratings (#) of Primary Book 1"]         = data.get("Book1_Num_Ratings", data.get("GoodReads_Rating_Count", "N/A"))
    df.at[idx, "Synopsis (if available)"]               = data.get("Description", "N/A")

# ------------------------------------------------------------------
# Process one row — opens a tab inside the shared context
# ------------------------------------------------------------------
async def process_row(context, scraper, df, idx, semaphore, excel_path, file_lock):
    async with semaphore:
        title  = str(df.at[idx, "Name of Series"]).strip()
        author = str(df.at[idx, "Author Name"]).strip()

        if title.lower() in ["", "nan"]:
            return

        print(f"  [Searching] '{title}' by {author}")

        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                save_book_data(df, idx, data)
                link = df.at[idx, "GoodReads series link"]
                rating = df.at[idx, "Rating (out of 5) of Primary Book 1"]
                print(f"  [OK] '{title}' -> {link} | Rating: {rating}")
            else:
                df.at[idx, "GoodReads series link"] = "N/A"
                print(f"  [Not Found] '{title}'")
        except Exception as e:
            print(f"  [Error] '{title}': {e}")
            df.at[idx, "GoodReads series link"] = "N/A"

        # Save after every single book
        async with file_lock:
            try:
                df.to_excel(excel_path, index=False)
            except Exception as save_err:
                print(f"  [Save Error] {save_err}")

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
async def scrape_root_literary(excel_path, book_limit=20):
    print(f"Loading: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: File not found - {excel_path}")
        return

    df = pd.read_excel(excel_path, keep_default_na=False)

    # Ensure target columns are object type
    for col in [
        "GoodReads series link",
        "Number of PRIMARY books in the series",
        "Rating (out of 5) of Primary Book 1",
        "Ratings (#) of Primary Book 1",
        "Synopsis (if available)",
    ]:
        if col in df.columns:
            df[col] = df[col].astype(object)

    # Pick the next N unscraped rows
    rows_to_process = []

    for idx, row in df.iterrows():
        title  = str(row.get("Name of Series", "")).strip()

        if not title or title.lower() in ["", "nan"]:
            continue

        # Skip already-scraped rows
        current_link = str(row.get("GoodReads series link", "")).strip()
        if current_link and current_link.lower() not in ["", "nan", "n/a"]:
            continue

        rows_to_process.append(idx)
        if len(rows_to_process) >= book_limit:
            break

    print(f"Books to scrape: {len(rows_to_process)}\n")

    if not rows_to_process:
        print("Nothing to scrape.")
        return

    file_lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(CONCURRENCY)
    scraper   = GoodreadsScraper(headless=False)

    async with async_playwright() as p:
        # ONE browser window
        browser = await p.chromium.launch(headless=False)
        # ONE shared context (all tabs live inside this)
        context = await browser.new_context()

        # Login once on a single tab, then close it
        print("[System] Logging in to Goodreads...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        print("[System] Login done. Starting scrape with 5 tabs...\n")

        # Dispatch all tasks — each opens its own tab inside context
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

    # Re-apply styling and open the file
    print("Reapplying styling...")
    apply_styling(excel_path)
    print("Opening file...")
    import subprocess
    subprocess.Popen(["start", excel_path], shell=True)
    print("Done!")


if __name__ == "__main__":
    base       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base, "Root_Literary_Formatted.xlsx")
    # Scrape the next 20 unscraped books
    asyncio.run(scrape_root_literary(excel_path, book_limit=50))
