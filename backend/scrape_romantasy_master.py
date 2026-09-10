import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

CSV_FILE = r"E:\Internship\PocketFM\Romantasy _ Self Publication Master - Romantasy Checker.csv"

async def process_row(index, row, context, scraper, df, excel_lock):
    series_name = str(row.get('Series Name', '')).strip()
    author = str(row.get('Author', '')).strip()
    gr_url = str(row.get('Book Series (GoodReads URL)', '')).strip()
    logline = str(row.get('Logline', '')).strip()

    is_missing_logline = pd.isna(row.get('Logline')) or logline == '' or logline == 'nan'
    is_missing_author = pd.isna(row.get('Author')) or author == '' or author == 'nan'
    is_missing_ratings = pd.isna(row.get('Goodreads Book 1 Ratings')) or str(row.get('Goodreads Book 1 Ratings')) == '' or str(row.get('Goodreads Book 1 Ratings')) == 'nan'
    is_missing_num_ratings = pd.isna(row.get('GoodReads No. of Ratings')) or str(row.get('GoodReads No. of Ratings')) == '' or str(row.get('GoodReads No. of Ratings')) == 'nan'
    is_missing_books = pd.isna(row.get('Total Primary Books')) or str(row.get('Total Primary Books')) == '' or str(row.get('Total Primary Books')) == 'nan'
    is_missing_pages = pd.isna(row.get('Total primary Books Page Count')) or str(row.get('Total primary Books Page Count')) == '' or str(row.get('Total primary Books Page Count')) == 'nan'

    if not (is_missing_logline or is_missing_author or is_missing_ratings or is_missing_num_ratings or is_missing_books or is_missing_pages):
        # Nothing missing, skip
        return

    print(f"\n[Row {index + 1}] Scraping for: {series_name} by {author}")

    # Use the goodreads scraper method
    details = await scraper.scrape_goodreads_data(context, title=series_name, author=author, existing_url=gr_url)

    if not details:
        print(f"  -> Failed to find details for {series_name}")
        return

    async with excel_lock:
        if is_missing_logline and details.get('Description', 'N/A') != 'N/A':
            df.at[index, 'Logline'] = details['Description']
            print("  -> Found Logline")
        if is_missing_author and details.get('Author_Found', 'Unknown') not in ['Unknown', 'N/A']:
            df.at[index, 'Author'] = details['Author_Found']
            print(f"  -> Found Author: {details['Author_Found']}")
        if is_missing_ratings and details.get('Book1_Rating', 'N/A') != 'N/A':
            df.at[index, 'Goodreads Book 1 Ratings'] = details['Book1_Rating']
        if is_missing_num_ratings and details.get('Book1_Num_Ratings', 'N/A') != 'N/A':
            df.at[index, 'GoodReads No. of Ratings'] = details['Book1_Num_Ratings']
        if is_missing_books and details.get('Num_Primary_Books', '1') not in ['1', 'N/A']:
            df.at[index, 'Total Primary Books'] = details['Num_Primary_Books']
        if is_missing_pages and details.get('Num_Pages', 'N/A') != 'N/A':
            df.at[index, 'Total primary Books Page Count'] = details['Num_Pages']

        df.to_csv(CSV_FILE, index=False)

async def main():
    print(f"Loading {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Failed to load CSV: {e}")
        return

    if 'Logline' not in df.columns:
        df['Logline'] = ""

    # Convert all columns we might write to to object type to prevent Pandas Dtype errors
    cols_to_convert = ['Logline', 'Author', 'Goodreads Book 1 Ratings', 'GoodReads No. of Ratings', 'Total Primary Books', 'Total primary Books Page Count']
    for col in cols_to_convert:
        if col in df.columns:
            df[col] = df[col].astype(object)

    # FOR TESTING: Limit to first 3 rows
    print("WARNING: Limiting to first 3 rows for testing as per the plan.")
    test_df = df.head(3)

    excel_lock = asyncio.Lock()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # Login Phase
        scraper = GoodreadsScraper(headless=False)
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()

        for idx, row in test_df.iterrows():
            # Run sequentially to avoid rate limits during testing
            await process_row(idx, row, context, scraper, df, excel_lock)

        await browser.close()

    print("\nTest scrape complete!")

if __name__ == "__main__":
    asyncio.run(main())
