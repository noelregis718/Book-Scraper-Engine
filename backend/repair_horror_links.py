import asyncio
import pandas as pd
import os
import sys
import random
from playwright.async_api import async_playwright

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from goodreads_scraper import GoodreadsScraper, normalize_title_for_search
from excel_utility import save_to_excel

# Configuration
INPUT_FILE = "Horror_-_Amazon_Keyword_Crawl (3).xlsx"
OUTPUT_FILE = "Horror_-_Amazon_Keyword_Crawl (3).xlsx"
MAX_CONCURRENT_TABS = 10
ROWS_TO_PROCESS = 20

async def validate_and_repair_link(index, row, context, semaphore, gr_scraper, df, total, counter):
    async with semaphore:
        counter[0] += 1
        curr = counter[0]
        
        excel_title = str(row.get("Title", "Unknown"))
        author = str(row.get("Author", ""))
        existing_url = str(row.get("Goodread Link", "N/A"))
        
        print(f"[{curr}/{total}] Verifying: {excel_title}...")
        
        needs_repair = False
        match_found = False
        
        # 1. Check if existing link works and title matches
        if existing_url and existing_url != "N/A" and "goodreads.com" in existing_url:
            page = await context.new_page()
            try:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                # Shorter timeout for opening the page to avoid getting stuck
                response = await page.goto(existing_url, wait_until="domcontentloaded", timeout=20000)
                
                if response and response.status < 400:
                    # Extract title from Goodreads page
                    gr_title_el = await page.query_selector('[data-testid="bookTitle"], #bookTitle')
                    if gr_title_el:
                        gr_title = (await gr_title_el.inner_text()).strip()
                        
                        # Normalize both for comparison
                        norm_excel = normalize_title_for_search(excel_title)
                        norm_gr = normalize_title_for_search(gr_title)
                        
                        if norm_excel in norm_gr or norm_gr in norm_excel:
                            print(f"  [Match] Title verified on page: {gr_title}")
                            match_found = True
                        else:
                            print(f"  [Mismatch] Page title '{gr_title}' does not match Excel '{excel_title}'.")
                            needs_repair = True
                    else:
                        print(f"  [Error] Could not find title on page.")
                        needs_repair = True
                else:
                    print(f"  [Error] Page returned status {response.status if response else 'None'}")
                    needs_repair = True
            except Exception as e:
                print(f"  [Error] Link failed to open: {e}")
                needs_repair = True
            finally:
                await page.close()
        else:
            needs_repair = True

        # User Requirement: If link didn't open or didn't match, clear it IMMEDIATELY
        if needs_repair and not match_found:
            cols_to_clear = [
                "Goodreads Rating", "Goodreads No. of Ratings", "Goodread Link",
                "Series Book 1", "Series Link", "# of primary books", "GR Book 1 Rating"
            ]
            for col in cols_to_clear:
                if col in df.columns:
                    df.at[index, col] = "" # Empty string for Excel
            print(f"  [Clean] Values cleared for '{excel_title}' (Broken/Mismatch)")

        # 2. Search if needed (if broken or mismatch)
        new_url = "" # Default to empty if not found
        if needs_repair and not match_found:
            print(f"  [Search] Attempting to find correct link for '{excel_title}'...")
            try:
                gr_data = await gr_scraper.scrape_goodreads_data(context, excel_title, author)
                if gr_data:
                    search_url = gr_data.get('GoodReads_Series_URL', 'N/A')
                    if search_url == "N/A":
                        search_url = gr_data.get('GoodReads_Book_URL', 'N/A')
                    
                    # Verify the searched book's title too
                    found_title = gr_data.get('Book_Title', '')
                    norm_excel = normalize_title_for_search(excel_title)
                    norm_found = normalize_title_for_search(found_title)
                    
                    if search_url != "N/A" and (norm_excel in norm_found or norm_found in norm_excel):
                        print(f"  [Found] Verified search result: {search_url}")
                        new_url = search_url
                        match_found = True
                        
                        # If found, put the new data back
                        df.at[index, "Goodread Link"] = new_url
                        # We could also update other gr_data fields here if needed
                    else:
                        print(f"  [Not Found] No valid match found during search.")
                else:
                    print(f"  [Not Found] Search returned no results.")
            except:
                pass

        # Final check: if still no match, ensure columns are empty
        if not match_found:
            # Already cleared above, but ensuring Goodread Link is empty
            df.at[index, "Goodread Link"] = ""


async def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(root_dir, INPUT_FILE)
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print(f"Loading {INPUT_FILE}...")
    df = pd.read_excel(file_path)
    
    # Target first 50 rows
    subset_df = df.head(ROWS_TO_PROCESS).copy()
    total = len(subset_df)
    
    print(f"Starting repair for first {total} rows with {MAX_CONCURRENT_TABS} concurrent tabs...")
    
    async with async_playwright() as p:
        # Launching with headless=False so user can see the login and tabs
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        gr_scraper = GoodreadsScraper(headless=False)
        
        # --- LOGIN STEP ---
        print("Starting Goodreads login process...")
        login_page = await context.new_page()
        login_success = await gr_scraper.login_to_goodreads(login_page)
        
        if login_success:
            print("Login successful! Waiting 5 seconds to settle...")
            await asyncio.sleep(5)
            await login_page.close()
        else:
            print("Login failed or requires manual intervention. Please check the browser.")
            # We don't exit, maybe it needs manual CAPTCHA solving
            await asyncio.sleep(10) 
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_TABS)
        counter = [0]
        
        tasks = []
        for index, row in subset_df.iterrows():
            tasks.append(validate_and_repair_link(index, row, context, semaphore, gr_scraper, df, total, counter))
        
        await asyncio.gather(*tasks)
        
        print(f"Repair complete. Saving to {OUTPUT_FILE}...")
        # Use excel_utility if available, or just df.to_excel
        try:
            from excel_utility import save_to_excel
            save_to_excel(df.to_dict('records'), file_path)
        except:
            df.to_excel(file_path, index=False)
            
        await browser.close()
        print("Done! Opening file...")
        if os.name == 'nt':
            os.startfile(file_path)

if __name__ == "__main__":
    asyncio.run(main())
