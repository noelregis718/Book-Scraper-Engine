import asyncio
import pandas as pd
import os
import sys
import re
from playwright.async_api import async_playwright

# --- CONFIGURATION ---
INPUT_FILE = r"E:\Internship\PocketFM\Your_Excel_File.xlsx" # UPDATE THIS
OUTPUT_FILE = r"E:\Internship\PocketFM\Your_Excel_File_Updated.xlsx" # UPDATE THIS
URL_COLUMN = "Goodreads URL" # UPDATE THIS TO EXACT COLUMN NAME

async def get_book_pages(page, url):
    """Scrapes number of pages from a single book URL."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(1.5) # Wait to prevent rate limiting
        
        # Check for CAPTCHA
        if await page.query_selector('#captcha-image, .captcha, iframe[src*="captcha"]'):
            print(f"    [!!! ACTION REQUIRED !!!] CAPTCHA detected for '{url}'! Please solve it in the browser window.")
            try:
                await page.wait_for_selector('[data-testid="pagesFormat"]', timeout=300000) # Wait up to 5 mins
            except:
                print(f"    [Timeout] CAPTCHA not solved in 5 minutes.")
                return 0

        # Selectors for pages on Goodreads
        page_format_el = await page.query_selector('[data-testid="pagesFormat"]')
        if page_format_el:
            text = await page_format_el.inner_text()
            match = re.search(r'(\d+)\s*pages', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Fallback for older goodreads layout
        page_format_el_old = await page.query_selector('span[itemprop="numberOfPages"]')
        if page_format_el_old:
            text = await page_format_el_old.inner_text()
            match = re.search(r'(\d+)', text)
            if match:
                return int(match.group(1))
                
        return 0
    except Exception as e:
        print(f"    Error scraping book page {url}: {e}")
        return 0

async def process_url(page, url):
    """Determine type of URL and get total pages."""
    if pd.isna(url) or not isinstance(url, str):
        return 0
        
    url = url.strip()
    if not url.startswith('http'):
        return 0
        
    if '/book/show/' in url:
        print(f"  [Book] Scraping pages...")
        return await get_book_pages(page, url)
        
    elif '/series/' in url:
        print(f"  [Series] Scraping individual books in series...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)
            book_links = await page.query_selector_all('.listWithDividers__item a.bookTitle, .listWithDividers__item a[href*="/book/show/"]')
            urls_to_visit = []
            for link in book_links:
                href = await link.evaluate("el => el.href")
                # Clean up goodreads relative/absolute URLs
                if href.startswith('/'):
                    href = f"https://www.goodreads.com{href}"
                urls_to_visit.append(href)
            
            urls_to_visit = list(set(urls_to_visit)) # De-duplicate
            total_pages = 0
            print(f"  Found {len(urls_to_visit)} books in series.")
            for b_url in urls_to_visit:
                pages = await get_book_pages(page, b_url)
                print(f"    - {pages} pages ({b_url})")
                total_pages += pages
            return total_pages
        except Exception as e:
            print(f"  Error scraping series {url}: {e}")
            return 0
            
    elif '/author/show/' in url:
        print(f"  [Author] Scraping all books by author...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)
            book_links = await page.query_selector_all('tr[itemtype="http://schema.org/Book"] a.bookTitle')
            urls_to_visit = []
            for link in book_links:
                href = await link.evaluate("el => el.href")
                if href.startswith('/'):
                    href = f"https://www.goodreads.com{href}"
                urls_to_visit.append(href)
            
            urls_to_visit = list(set(urls_to_visit))
            total_pages = 0
            print(f"  Found {len(urls_to_visit)} books for author.")
            for b_url in urls_to_visit:
                pages = await get_book_pages(page, b_url)
                print(f"    - {pages} pages ({b_url})")
                total_pages += pages
            return total_pages
        except Exception as e:
            print(f"  Error scraping author {url}: {e}")
            return 0
    else:
        print(f"  Unsupported URL type: {url}")
        return 0


async def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        print("Please open 'scrape_goodreads_pages.py' and update the INPUT_FILE path.")
        return
        
    df = pd.read_excel(INPUT_FILE)
    if URL_COLUMN not in df.columns:
        print(f"Column '{URL_COLUMN}' not found in Excel sheet. Available columns: {list(df.columns)}")
        print("Please update the URL_COLUMN variable in 'scrape_goodreads_pages.py'.")
        return

    # Add output columns if they don't exist
    if 'Total Pages' not in df.columns:
        df['Total Pages'] = 0
    if 'Calculated Score' not in df.columns:
        df['Calculated Score'] = 0.0
    if 'Flag' not in df.columns:
        df['Flag'] = ""

    async with async_playwright() as p:
        # Headless=False so the browser window opens. This is crucial for solving GoodReads CAPTCHAs!
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for index, row in df.iterrows():
            url = row[URL_COLUMN]
            print(f"\nProcessing row {index + 1}/{len(df)}: {url}")
            
            # Skip if already processed
            if pd.notna(row.get('Total Pages')) and row.get('Total Pages') != 0:
                print("  Skipping: Already processed (Total Pages > 0)")
                continue

            total_pages = await process_url(page, url)
            
            # Calculate formula: Total Pages * 250 / 10000
            score = (total_pages * 250) / 10000
            
            # Determine Flag: if score <= 40
            flag = "Yes" if (score <= 40 and score > 0) else "No"
            if total_pages == 0:
                flag = "N/A" # Could not scrape pages
            
            df.at[index, 'Total Pages'] = total_pages
            df.at[index, 'Calculated Score'] = score
            df.at[index, 'Flag'] = flag
            
            print(f"  => Total Pages: {total_pages}, Score: {score}, Flag: {flag}")
            
            # Save progress every 5 rows
            if (index + 1) % 5 == 0:
                df.to_excel(OUTPUT_FILE, index=False)
                print(f"  [Saved progress to {OUTPUT_FILE}]")

        await browser.close()

    # Final save
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nFinished processing! Final data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
