import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper, normalize_title_for_search
from apply_jra_style import apply_styling

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "Next_Agency.xlsx"

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)
file_lock = asyncio.Lock()

async def safe_save(df):
    async with file_lock:
        try:
            df.to_excel(EXCEL_FILE, index=False)
        except Exception as e:
            print(f"Error saving excel: {e}", flush=True)

async def scrape_author_for_book(index, row, df, context, semaphore):
    title = str(row.get("Name of Series", "")).strip()
    current_author = str(row.get("Author Name", "")).strip()
    
    # Only process if Author is missing
    if current_author and current_author.lower() != "nan" and current_author != "":
        return

    if not title or title.lower() == "nan":
        return

    async with semaphore:
        print(f"[{index}] Searching Goodreads for missing author of: '{title}'", flush=True)
        page = await context.new_page()
        try:
            clean_title = normalize_title_for_search(title)
            search_url = f"https://www.goodreads.com/search?q={clean_title.replace(' ', '+')}"
            
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)
            
            # The author name on the search page is inside <a class="authorName">
            author_el = await page.query_selector('.authorName[itemprop="url"] span[itemprop="name"]')
            if not author_el:
                author_el = await page.query_selector('.authorName')
                
            if author_el:
                author_name = (await author_el.inner_text()).strip()
                if author_name:
                    print(f"[{index}] Found Author: {author_name} for '{title}'", flush=True)
                    df.at[index, "Author Name"] = author_name
                    await safe_save(df)
                else:
                    print(f"[{index}] Author element found but empty for '{title}'", flush=True)
            else:
                print(f"[{index}] Could not find author for '{title}' in search results.", flush=True)
                
        except Exception as e:
            print(f"[{index}] Error searching '{title}': {e}", flush=True)
        finally:
            await page.close()

async def run():
    print(f"Loading Excel file: {EXCEL_FILE}", flush=True)
    df = pd.read_excel(EXCEL_FILE)
    
    missing_count = sum(df['Author Name'].isna() | (df['Author Name'] == ''))
    print(f"Found {missing_count} books missing authors.", flush=True)
    
    if missing_count == 0:
        print("No missing authors to scrape!")
        return

    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(10) # 10 concurrent tabs
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login to avoid search blocks
        await scraper.login_to_goodreads(page)
        await page.close()
        
        print("\nStarting fast Author extraction...", flush=True)
        tasks = []
        for index, row in df.iterrows():
            tasks.append(scrape_author_for_book(index, row, df, context, semaphore))
            
        await asyncio.gather(*tasks)
        await browser.close()
        
    print("\nAuthor Scraping complete.", flush=True)
    try:
        apply_styling(EXCEL_FILE)
        print("Styling applied.", flush=True)
    except: pass

if __name__ == "__main__":
    asyncio.run(run())
