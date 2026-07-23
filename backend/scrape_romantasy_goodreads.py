import asyncio
import pandas as pd
import re
import os
import subprocess
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

INPUT_FILE = r"e:\Internship\PocketFM\Romantasy_v2_extracted.xlsx"
OUTPUT_FILE = r"e:\Internship\PocketFM\Romantasy_v2_extracted.xlsx"

async def solve_captcha_if_present(page, url=""):
    try:
        if await page.query_selector('#captcha-image, .captcha, iframe[src*="captcha"]'):
            print(f"    [!!!] CAPTCHA detected! Please solve it manually.")
            try:
                await page.wait_for_selector('a.bookTitle, [data-testid="pagesFormat"], .listWithDividers__item, h1', timeout=120000)
                print(f"    [Success] CAPTCHA solved.")
            except:
                print(f"    [Timeout] CAPTCHA wait timeout.")
    except Exception:
        pass

async def search_book_on_goodreads(page, title, author):
    """Searches Goodreads and returns the URL of the first book result."""
    search_term = f"{title} {author}".strip()
    if not search_term:
        return None
        
    search_url = f"https://www.goodreads.com/search?q={search_term.replace(' ', '+')}"
    print(f"    Searching Goodreads: {search_url}")
    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        await solve_captcha_if_present(page, search_url)
        
        # Click the first book result
        first_result = await page.query_selector('a.bookTitle')
        if first_result:
            b_url = await first_result.evaluate("el => el.href")
            if b_url.startswith('/'):
                b_url = f"https://www.goodreads.com{b_url}"
            return b_url
    except Exception as e:
        print(f"    Error searching for {search_term}: {e}")
    return None

async def get_book_pages(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(1.5)
        await solve_captcha_if_present(page, url)
        
        content = await page.content()
        match = re.search(r'"numPages":(\d+)', content)
        if match:
            return int(match.group(1))
            
        match = re.search(r'>(\d+)\s*pages', content, re.IGNORECASE)
        if match:
            return int(match.group(1))
            
        return 0
    except Exception as e:
        print(f"    Error scraping book page {url}: {e}")
        return 0

async def get_series_pages(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        await solve_captcha_if_present(page, url)
        
        book_links = await page.query_selector_all('.listWithDividers__item a.bookTitle, .listWithDividers__item a[href*="/book/show/"]')
        urls_to_visit = []
        for link in book_links:
            href = await link.evaluate("el => el.href")
            if href.startswith('/'):
                href = f"https://www.goodreads.com{href}"
            urls_to_visit.append(href)
        
        urls_to_visit = list(set(urls_to_visit))
        total_pages = 0
        num_books = len(urls_to_visit)
        print(f"    Found {num_books} books in series.")
        
        for b_url in urls_to_visit:
            pages = await get_book_pages(page, b_url)
            print(f"      - {pages} pages ({b_url})")
            total_pages += pages
            
        return num_books, total_pages
    except Exception as e:
        print(f"    Error scraping series {url}: {e}")
        return 0, 0

async def process_row(index, row, context, df, semaphore, excel_lock, required_cols):
    book1_link = str(row.get('GR Book 1 link', '')).strip()
    series_link = str(row.get('GR Series Link', '')).strip()
    num_books = row.get('No. of books in the series', pd.NA)
    page_count = row.get('Page count', pd.NA)
    
    title = str(row.get('Title', '')).strip()
    author = str(row.get('Author Name', '')).strip()
    
    is_missing_books = pd.isna(num_books) or str(num_books).strip() in ['', 'nan', '0', '0.0']
    is_missing_pages = pd.isna(page_count) or str(page_count).strip() in ['', 'nan', '0', '0.0']
    is_missing_series = series_link == '' or series_link.lower() == 'nan' or 'missing' in series_link.lower()
    
    needs_scrape = is_missing_series or is_missing_books or is_missing_pages
    
    if not needs_scrape:
        return
        
    async with semaphore:
        print(f"\n[Row {index}] Starting scrape.")
        page = await context.new_page()
        try:
            # 1. Try to use Series Link directly if available
            if not is_missing_series and series_link.startswith('http'):
                print(f"  [Row {index}] Scraping directly from Series Link: {series_link}")
                books_count, pages_total = await get_series_pages(page, series_link)
                async with excel_lock:
                    df.at[index, 'No. of books in the series'] = books_count
                    df.at[index, 'Page count'] = pages_total
            else:
                # 2. Try Book 1 link, or search if Book 1 link is missing
                target_book_link = book1_link
                if not target_book_link.startswith('http'):
                    print(f"  [Row {index}] Both links missing. Searching for '{title} {author}'...")
                    found_link = await search_book_on_goodreads(page, title, author)
                    if found_link:
                        target_book_link = found_link
                        print(f"  [Row {index}] Found Book 1 Link: {target_book_link}")
                        async with excel_lock:
                            df.at[index, 'GR Book 1 link'] = target_book_link
                    else:
                        print(f"  [Row {index}] Search yielded no results.")
                
                # 3. If we have a Book 1 link, find the Series link
                if target_book_link.startswith('http'):
                    await page.goto(target_book_link, wait_until="domcontentloaded", timeout=60000)
                    await asyncio.sleep(2)
                    await solve_captcha_if_present(page, target_book_link)
                    
                    found_series_link = None
                    b_series = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a, h2 a[href*="/series/"]')
                    if b_series:
                        found_series_link = await b_series.evaluate("el => el.href")
                        if found_series_link.startswith('/'):
                            found_series_link = "https://www.goodreads.com" + found_series_link
                            
                    if found_series_link:
                        print(f"  [Row {index}] Found Series Link: {found_series_link}")
                        async with excel_lock:
                            df.at[index, 'GR Series Link'] = found_series_link
                        
                        books_count, pages_total = await get_series_pages(page, found_series_link)
                        async with excel_lock:
                            df.at[index, 'No. of books in the series'] = books_count
                            df.at[index, 'Page count'] = pages_total
                    else:
                        print(f"  [Row {index}] No Series Link found. Treating as standalone.")
                        pages = await get_book_pages(page, target_book_link)
                        async with excel_lock:
                            df.at[index, 'No. of books in the series'] = 1
                            df.at[index, 'Page count'] = pages
                            df.at[index, 'GR Series Link'] = "N/A"
                            
            # Save progress incrementally
            async with excel_lock:
                # Save all columns
                df.to_excel(OUTPUT_FILE, index=False)
                
        except Exception as e:
            print(f"  [Row {index}] Failed to process: {e}")
        finally:
            await page.close()

async def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return
        
    print(f"Loading {INPUT_FILE}...")
    df = pd.read_excel(INPUT_FILE, header=0) 
    
    required_cols = [
        'GR Book 1 link',
        'Agency (if)',
        'GR Series Link',
        'No. of books in the series',
        'Page count'
    ]
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = ''
            
    semaphore = asyncio.Semaphore(1)
    excel_lock = asyncio.Lock()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # --- LOGIN PHASE ---
        print("Starting Login Phase...")
        login_page = await context.new_page()
        scraper = GoodreadsScraper(headless=False)
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        print("Login complete. Starting concurrent scrape...")
        
        # --- SCRAPING PHASE ---
        tasks = []
        for index, row in df.iterrows():
            if index < 61: # Skip to row 63
                continue
            tasks.append(process_row(index, row, context, df, semaphore, excel_lock, required_cols))
            
        await asyncio.gather(*tasks)
        
        await browser.close()
    
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Scraping fully complete. Saved to {OUTPUT_FILE}")
    
    # Trigger styling (make sure styling script applies to the correct file)
    # The merge styling handles this, but since we updated it, we can just call merge_scraped_data logic if needed.
    # Actually, the user can style it later. For now we just preserve the file.

if __name__ == "__main__":
    asyncio.run(main())
