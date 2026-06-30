import asyncio
import pandas as pd
import os
import sys
import re
from playwright.async_api import async_playwright

# --- CONFIGURATION ---
INPUT_FILE = r"E:\Internship\PocketFM\Crime_Thriller_Amazon_Base_List - Series Base - 800 Titles (2).csv"
OUTPUT_FILE = r"E:\Internship\PocketFM\Crime_Thriller_Amazon_Base_List - Series Base - 800 Titles (2).csv"

# The script will use the URL column if it exists. 
URL_COLUMN = "Amazon URL" 
RATINGS_COLUMN = "Amazon Ratings"

async def solve_captcha_if_present(page, url):
    """Wait for user to manually solve Amazon CAPTCHA if it appears."""
    try:
        captcha_el = await page.query_selector('form[action="/errors/validateCaptcha"]')
        if captcha_el:
            print(f"\n    [!!! ACTION REQUIRED !!!] Amazon CAPTCHA detected!")
            print(f"    Please solve it in the open browser window.")
            # Wait until the captcha form is gone (meaning solved) or timeout
            await page.wait_for_selector('form[action="/errors/validateCaptcha"]', state="hidden", timeout=300000)
            print("    [Success] CAPTCHA solved.")
            await asyncio.sleep(2) # Give it a moment to load the actual page
    except Exception as e:
        pass # No captcha or error checking for it

async def extract_amazon_data(page):
    """Extract rating and total reviews from a loaded Amazon book page."""
    data = {"Total Ratings": 0}
    try:
        # Extract Total Ratings (e.g., "1,234 ratings")
        count_el = await page.query_selector('#acrCustomerReviewText, [data-hook="total-review-count"]')
        if count_el:
            text = await count_el.inner_text()
            match = re.search(r'([\d,]+)', text)
            if match:
                data["Total Ratings"] = int(match.group(1).replace(',', ''))
    except Exception as e:
        print(f"    Error extracting data from Amazon page: {e}")
    return data

async def process_row(page, row):
    """Navigate to Amazon URL and extract data."""
    data = {"Total Ratings": 0}
    url = row.get(URL_COLUMN, "") if URL_COLUMN in row else ""
    
    if pd.notna(url) and isinstance(url, str) and url.startswith('http'):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(1.5)
            await solve_captcha_if_present(page, url)
            return await extract_amazon_data(page)
        except Exception as e:
            print(f"    Error navigating to URL {url}: {e}")
            return data
    return data

async def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return
        
    if INPUT_FILE.endswith('.csv'):
        df = pd.read_csv(INPUT_FILE, encoding='utf-8')
    else:
        df = pd.read_excel(INPUT_FILE)

    if URL_COLUMN not in df.columns:
        print(f"Column '{URL_COLUMN}' not found.")
        return

    if RATINGS_COLUMN not in df.columns:
        df[RATINGS_COLUMN] = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for index, row in df.iterrows():
            url = row[URL_COLUMN]
            
            # Skip if no URL
            if pd.isna(url) or not isinstance(url, str):
                continue
                
            # If the Ratings column is missing or NA, or the user wants to rescrape, let's process it.
            # Removed row limit to process all titles
            print(f"\nProcessing row {index + 1}: {url}")
            extracted = await process_row(page, row)
            
            df.at[index, RATINGS_COLUMN] = extracted["Total Ratings"]
            print(f"  => Updated Total Ratings: {extracted['Total Ratings']}")
            
            if (index + 1) % 5 == 0:
                try:
                    if OUTPUT_FILE.endswith('.csv'):
                        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
                    else:
                        df.to_excel(OUTPUT_FILE, index=False)
                except PermissionError:
                    print(f"    [WARNING] Cannot save to {OUTPUT_FILE} because it is open in another program (like Excel). Please close it.")

        await browser.close()

    try:
        if OUTPUT_FILE.endswith('.csv'):
            df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        else:
            df.to_excel(OUTPUT_FILE, index=False)
        print(f"\nFinished processing! Data saved.")
    except PermissionError:
        print(f"\n[ERROR] Failed to save final data. The file {OUTPUT_FILE} is open in another program. Please close it and run again.")

if __name__ == "__main__":
    asyncio.run(main())
