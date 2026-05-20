import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scrape_tobias_goodreads import scrape_one_book
from goodreads_scraper import GoodreadsScraper
from apply_jra_style import apply_styling

async def scrape_ps(excel_path, limit=40):
    print(f"Loading: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: File not found — {excel_path}")
        return

    df = pd.read_excel(excel_path, keep_default_na=False)

    for col in ["GoodReads series link", "Number of PRIMARY books in the series",
                "Rating (out of 5) of Primary Book 1", "Ratings (#) of Primary Book 1",
                "Synopsis (if available)"]:
        if col in df.columns:
            df[col] = df[col].astype(object)

    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(10)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        login_context = await browser.new_context()
        login_page = await login_context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        storage_state = await login_context.storage_state()
        await login_context.close()
        print("Login done. Starting scrape...\n")

        tasks = []
        count = 0
        for index, row in df.iterrows():
            if count >= limit:
                break

            title = str(row.get("Name of Series", "")).strip()
            author = str(row.get("Author Name", "")).strip()

            if not title or title in ["nan", ""]:
                continue

            current_link = str(row.get("GoodReads series link", "")).strip()
            if current_link and current_link.lower() != "nan":
                continue

            if author in ["nan", "", "Unknown", "Unknown – pre-pub / unannounced"]:
                author_for_search = ""
            else:
                author_for_search = author

            tasks.append(scrape_one_book(index, title, author_for_search, df, excel_path, scraper, browser, storage_state, semaphore))
            count += 1

        await asyncio.gather(*tasks)
        print("\nScraping complete!")
        try:
            await browser.close()
        except: pass

    print("Reapplying styling...")
    apply_styling(excel_path)
    import subprocess
    subprocess.Popen(["start", excel_path], shell=True)
    print("All done!")

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(base, "New_Agency.xlsx")
    asyncio.run(scrape_ps(target, limit=60))
