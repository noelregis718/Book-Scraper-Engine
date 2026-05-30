import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper, clean_text
import re
import json

file_lock = asyncio.Lock()

async def safe_save(df, excel_path):
    async with file_lock:
        try:
            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"  [Save Error] {e}")

async def scrape_details_for_row(index, title, book_url, df, excel_path, browser, storage_state, semaphore):
    async with semaphore:
        context = await browser.new_context(storage_state=storage_state)
        page = await context.new_page()
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        try:
            print(f"[{index+2}] Navigating to: {title}")
            await page.goto(book_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(1.5)

            # --- Extract data ---
            avg_rating, rating_count = "N/A", "N/A"
            try:
                ld_el = await page.query_selector('script[type="application/ld+json"]')
                if ld_el:
                    ld_data = json.loads(await ld_el.inner_text())
                    if isinstance(ld_data, list): ld_data = ld_data[0]
                    avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                    rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
            except: pass

            description = "N/A"
            desc_el = await page.query_selector('[data-testid="description"] .Formatted, .readable')
            if desc_el:
                description = clean_text(await desc_el.inner_text())

            # Series link
            series_url = book_url  # fallback to book url
            series_link_el = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
            if series_link_el:
                series_url = await series_link_el.evaluate("el => el.href")

            # Primary books count from series page
            num_primary = "1"
            book1_rating = avg_rating
            book1_ratings = rating_count
            if "/series/" in series_url:
                try:
                    await page.goto(series_url, wait_until="domcontentloaded", timeout=45000)
                    content = await page.content()
                    m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
                    if m: num_primary = m.group(1)
                    row1 = await page.query_selector('.listWithDividers__item, .seriesWork')
                    if row1:
                        rtxt = (await row1.inner_text()).lower()
                        r_match = re.search(r'([\d.]+)\s+avg\s+rating\s+[—\-]\s+([\d,]+)\s+ratings', rtxt)
                        if r_match:
                            book1_rating = r_match.group(1)
                            book1_ratings = r_match.group(2).replace(',', '')
                except: pass

            # Save to dataframe
            df.at[index, "GoodReads series link"] = series_url
            df.at[index, "Number of PRIMARY books in the series"] = num_primary
            df.at[index, "Rating (out of 5) of Primary Book 1"] = book1_rating
            df.at[index, "Ratings (#) of Primary Book 1"] = book1_ratings
            df.at[index, "Synopsis (if available)"] = description

            print(f"[{index+2}] Extracted details for '{title}'")
            await safe_save(df, excel_path)

        except Exception as e:
            print(f"[{index+2}] Error on '{title}': {e}")
        finally:
            try:
                await context.close()
            except: pass

async def main(excel_path):
    print(f"Loading Excel file: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found: {excel_path}")
        return

    df = pd.read_excel(excel_path)
    
    # Target columns need to be object type
    cols_to_update = [
        "GoodReads series link", 
        "Number of PRIMARY books in the series",
        "Rating (out of 5) of Primary Book 1", 
        "Ratings (#) of Primary Book 1",
        "Synopsis (if available)"
    ]
    for col in cols_to_update:
        if col in df.columns:
            df[col] = df[col].astype(object)
        else:
            df[col] = "N/A"
            df[col] = df[col].astype(object)
            
    title_col = next((col for col in df.columns if 'title' in str(col).lower() or 'series' in str(col).lower() or 'book' in str(col).lower()), None)
    
    if not title_col:
        print("Error: Could not find title column.")
        return

    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(10) # 10 concurrent tabs
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        # Login once, save cookies
        login_context = await browser.new_context()
        login_page = await login_context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        storage_state = await login_context.storage_state()
        await login_context.close()
        print("Login complete. Starting details extraction...\n")

        tasks = []
        for index, row in df.iterrows():
            # We want to scrape where we previously marked as N/A or empty
            synopsis = str(row.get("Synopsis (if available)", "")).strip()
            if synopsis and synopsis.lower() not in ["nan", "none", "", "n/a"]:
                continue # Already has a synopsis

            book_url = str(row.get("GoodReads series link", "")).strip()
            if not book_url or not book_url.startswith("http"):
                continue # Need a link to scrape

            title = str(row.get(title_col, f"Row {index+2}")).strip()
            
            tasks.append(scrape_details_for_row(
                index, title, book_url, df, excel_path, 
                browser, storage_state, semaphore
            ))

        print(f"Found {len(tasks)} books that need details extracted.")
        await asyncio.gather(*tasks)

        await browser.close()
        
    print(f"\nFinished extracting all missing details. Saved to {excel_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_excel = sys.argv[1]
    else:
        target_excel = input("Please enter the path to the Excel file: ").strip()
    asyncio.run(main(target_excel))
