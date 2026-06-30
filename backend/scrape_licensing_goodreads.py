import asyncio
import pandas as pd
import os
import re
from playwright.async_api import async_playwright

# --- CONFIGURATION ---
INPUT_FILE = r"E:\Internship\PocketFM\Licensing _ Commissioning - Personal - Vikrant.xlsx"
OUTPUT_FILE = r"E:\Internship\PocketFM\Licensing _ Commissioning - Personal - Vikrant.xlsx"
SHEET_NAME = "Agencies"
START_ROW_EXCEL = 11  # Excel row 11

async def solve_captcha_if_present(page, url=""):
    """Wait for user to manually solve Goodreads CAPTCHA if it appears."""
    try:
        if await page.query_selector('#captcha-image, .captcha, iframe[src*="captcha"]'):
            print(f"    [!!! ACTION REQUIRED !!!] CAPTCHA detected! Please solve it in the browser window.")
            try:
                # Wait for a typical goodreads element to appear, indicating captcha is solved
                await page.wait_for_selector('a.bookTitle, [data-testid="pagesFormat"], .listWithDividers__item', timeout=300000)
                print("    [Success] CAPTCHA solved.")
            except:
                print(f"    [Timeout] CAPTCHA not solved in 5 minutes.")
    except Exception:
        pass


async def get_book_pages(page, url):
    """Scrapes number of pages from a single book URL."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(1.5) 
        await solve_captcha_if_present(page, url)

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


async def get_series_pages(page, url):
    """Scrapes all books in a series and sums their pages."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        await solve_captcha_if_present(page, url)
        
        # Find all books in the series
        book_links = await page.query_selector_all('.listWithDividers__item a.bookTitle, .listWithDividers__item a[href*="/book/show/"]')
        urls_to_visit = []
        for link in book_links:
            href = await link.evaluate("el => el.href")
            if href.startswith('/'):
                href = f"https://www.goodreads.com{href}"
            urls_to_visit.append(href)
        
        urls_to_visit = list(set(urls_to_visit))
        total_pages = 0
        print(f"    Found {len(urls_to_visit)} books in series.")
        
        for b_url in urls_to_visit:
            pages = await get_book_pages(page, b_url)
            print(f"      - {pages} pages ({b_url})")
            total_pages += pages
            
        return total_pages
    except Exception as e:
        print(f"    Error scraping series {url}: {e}")
        return 0


async def search_and_get_series_pages(page, search_term):
    """Searches Goodreads for the series and scrapes it."""
    try:
        print(f"    Searching Goodreads for: {search_term}")
        search_url = f"https://www.goodreads.com/search?q={search_term.replace(' ', '+')}"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        await solve_captcha_if_present(page, search_url)
        
        # Look for series links in search results
        series_link = await page.query_selector('a[href*="/series/"]')
        if series_link:
            s_url = await series_link.evaluate("el => el.href")
            if s_url.startswith('/'):
                s_url = "https://www.goodreads.com" + s_url
            print(f"    Found series link from search: {s_url}")
            return await get_series_pages(page, s_url)
        else:
            # Fallback: click first book, then find series link on book page
            book_link = await page.query_selector('a.bookTitle')
            if book_link:
                b_url = await book_link.evaluate("el => el.href")
                if b_url.startswith('/'):
                    b_url = "https://www.goodreads.com" + b_url
                print(f"    No direct series link in search. Going to first book: {b_url}")
                await page.goto(b_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(2)
                await solve_captcha_if_present(page, b_url)
                
                # Check for series link on book page
                b_series = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
                if b_series:
                    bs_url = await b_series.evaluate("el => el.href")
                    print(f"    Found series link on book page: {bs_url}")
                    return await get_series_pages(page, bs_url)
                else:
                    print("    No series link found on book page. Scraping just this book.")
                    pages = await get_book_pages(page, page.url)
                    print(f"      - {pages} pages ({page.url})")
                    return pages
            print("    No relevant search results found.")
            return 0
    except Exception as e:
        print(f"    Error searching for {search_term}: {e}")
        return 0


async def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return
        
    print(f"Loading {INPUT_FILE}...")
    # header=1 means Row 2 is the column names (0-indexed)
    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME, header=1)
    
    # Calculate pandas index for Excel row 11
    # Excel Row 1 = None, Row 2 = Header (index -1), Row 3 = Data Index 0
    # Excel Row 11 = Data Index 8
    start_index = START_ROW_EXCEL - 3 
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for index, row in df.iterrows():
            if index < start_index:
                continue
                
            excel_row_num = index + 3
            series_title = row.get('Series Title', '')
            num_books_val = row.get('No. of Books')
            gr_link = row.get('Goodreads Link', '')
            
            # Clean up number of books
            try:
                num_books = float(num_books_val)
            except (ValueError, TypeError):
                num_books = 999  # Skip if invalid or missing
                
            if num_books <= 5:
                print(f"\n[Row {excel_row_num}] '{series_title}' has {num_books} books (<= 5). Scraping...")
                
                total_pages = 0
                
                # Check if goodreads link is present and valid
                if pd.notna(gr_link) and isinstance(gr_link, str) and gr_link.startswith('http'):
                    if '/series/' in gr_link:
                        print(f"  Using direct Series URL: {gr_link}")
                        total_pages = await get_series_pages(page, gr_link)
                    else:
                        print(f"  URL is not a series link, falling back to search.")
                        total_pages = await search_and_get_series_pages(page, str(series_title))
                else:
                    print(f"  No valid Goodreads URL found. Searching by Series Title...")
                    if pd.notna(series_title) and str(series_title).strip():
                        total_pages = await search_and_get_series_pages(page, str(series_title))
                    else:
                        print("  No Series Title available to search.")
                
                print(f"  => Total Pages for Series: {total_pages}")
                
                # Apply Benchmark logic
                if 0 < total_pages < 1600:
                    print(f"  => [FLAG] Pages ({total_pages}) < 1600. Flagging 'pages less'")
                    df.at[index, 'Subj. Review / Remarks'] = 'pages less'
                elif total_pages >= 1600:
                    print(f"  => Pages ({total_pages}) >= 1600. No flag needed.")
                
                # Save progress periodically
                if (index + 1) % 2 == 0:
                    try:
                        # We must preserve the original file structure if possible. 
                        # Pandas will overwrite the whole file, removing other sheets if we just use to_excel.
                        # To update a specific sheet while keeping others, we use ExcelWriter with mode='a' and if_sheet_exists='replace'
                        with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                            df.to_excel(writer, sheet_name=SHEET_NAME, index=False, header=True, startrow=1)
                    except Exception as e:
                        print(f"  [Warning] Couldn't save incremental progress. Is the file open? Error: {e}")
            else:
                pass # print(f"Row {excel_row_num} skipped ({num_books} books)")

        await browser.close()

    # Final Save
    try:
        print("\nSaving final results...")
        with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            # We want to preserve the empty first row that acts as a gap, but pandas index=False writes from row 1.
            # Writing with startrow=1 means the header goes to Excel row 2.
            df.to_excel(writer, sheet_name=SHEET_NAME, index=False, header=True, startrow=1)
        print(f"Finished processing! Saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"[Error] Failed to save final data: {e}")

if __name__ == "__main__":
    asyncio.run(main())
