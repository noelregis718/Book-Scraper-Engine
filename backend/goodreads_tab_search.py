import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os

# Configuration
CATALOG_FILE = "Speilburg_Media_Catalog_Final.xlsx"
BATCH_SIZE = 10 # Opens 10 tabs at a time

async def search_in_tab(context, series_name, author_name):
    print(f"  [Tab] Searching for: {series_name} by {author_name}...")
    page = await context.new_page()
    try:
        # Go to Goodreads Search
        search_query = f"{series_name} {author_name}"
        await page.goto(f"https://www.goodreads.com/search?q={search_query}")
        
        # Wait for results to load
        await page.wait_for_selector(".searchSubNav", timeout=10000)
        print(f"  [Tab] Results loaded for: {series_name}")
        
        # We keep the tab open for the user to see/interact if needed
        # Or you can add scraping logic here later
    except Exception as e:
        print(f"  [Tab] Error searching for {series_name}: {e}")

async def run_tabbed_search():
    if not os.path.exists(CATALOG_FILE):
        print(f"Error: {CATALOG_FILE} not found!")
        return

    # Load data
    df = pd.read_excel(CATALOG_FILE)
    rows = df[['Name of Series', 'Author Name']].dropna().values.tolist()
    
    print(f"Total entries to search: {len(rows)}")

    async with async_playwright() as p:
        # Launch browser in HEADED mode so the user can see the 10 tabs
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Login (Optional but recommended)
        print("[System] Opening login page... Please ensure you are logged in.")
        login_page = await context.new_page()
        await login_page.goto("https://www.goodreads.com/user/sign_in")
        print("[System] Waiting 30 seconds for you to check login status...")
        await asyncio.sleep(30)
        await login_page.close()

        # Process in batches of 10
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i:i+BATCH_SIZE]
            print(f"\n>>> Launching Batch {(i//BATCH_SIZE)+1} (10 Tabs)...")
            
            tasks = []
            for series, author in batch:
                tasks.append(search_in_tab(context, series, author))
            
            await asyncio.gather(*tasks)
            
            input("\nBatch loaded in 10 tabs. Press Enter in this console to CLOSE these tabs and load the NEXT 10...")
            
            # Close all pages except the default one if any
            for page in context.pages:
                await page.close()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tabbed_search())
