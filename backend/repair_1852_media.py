import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os
import json
import random
import re
import sys
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

# Fix console encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Configuration
MASTER_FILE = "Deep_Catalog_Enrichment.xlsx"
CONCURRENCY_LIMIT = 1 

# Target Authors and their "broken" row ranges (0-indexed)
TARGETS = {
    "Melissa Foster": {"start": 1308, "end": 1571}, # Covers 1309-1322 and 1565-1572 (handles everything in between too)
    "VF Mason": {"start": 1542, "end": 1549}        # Rows 1543-1550
}

def normalize(t):
    if not t: return ""
    return re.sub(r'\(.*?\)', '', str(t)).strip().lower()

async def get_all_author_book_links(page, author_name, existing_books):
    """Aggressive discovery of ALL books for an author."""
    print(f"  [Discovery] Finding full catalog for: {author_name}", flush=True)
    try:
        # We'll try to find the "All Books" link directly if possible
        search_url = f"https://www.goodreads.com/search?q={author_name.replace(' ', '+')}&search_type=books"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        
        author_link = await page.query_selector('a[href*="/author/show/"]')
        if not author_link:
            print(f"    [Error] Could not find author link for {author_name}", flush=True)
            return []
            
        author_url = await author_link.evaluate("el => el.href")
        all_books_url = author_url.replace("/show/", "/list/")
        if "?" in all_books_url:
            all_books_url = all_books_url.split("?")[0]
            
        all_links = []
        current_page = 1
        
        # Increase pagination limit to 30 for authors with massive catalogs
        while current_page <= 30:
            print(f"    [Pagination] Scraping Page {current_page}...", flush=True)
            try:
                await page.goto(f"{all_books_url}?page={current_page}", wait_until="domcontentloaded", timeout=90000)
                await asyncio.sleep(2)
                
                book_els = await page.query_selector_all('a.bookTitle')
                page_found = 0
                for el in book_els:
                    title = await el.evaluate("el => el.innerText")
                    link = await el.evaluate("el => el.href")
                    if link and title:
                        clean_link = link.split('?')[0]
                        norm_title = normalize(title)
                        if norm_title not in existing_books:
                            if clean_link not in all_links:
                                all_links.append(clean_link)
                                page_found += 1
                                safe_title = title.encode('ascii', 'replace').decode('ascii')
                                print(f"    [Discovery] Found new title: {safe_title}", flush=True)
                
                print(f"      Found {page_found} new unique titles on this page.", flush=True)
                
                next_btn = await page.query_selector('a.next_page')
                if not next_btn:
                    break
                current_page += 1
            except Exception as pe:
                print(f"      [Warning] Timeout or error on page {current_page}: {pe}", flush=True)
                break
            
        print(f"    [Discovery Complete] Found {len(all_links)} total unique books for {author_name}.", flush=True)
        return all_links
    except Exception as e:
        print(f"    [Error] Discovery failed for {author_name}: {e}", flush=True)
        return all_links

async def scrape_book_details(context, scraper, link, author_name):
    try:
        page = await context.new_page()
        # Set realistic headers
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        print(f"    [Scraper] Visiting: {link}", flush=True)
        await page.goto(link, wait_until="domcontentloaded", timeout=60000)
        data = await scraper.extract_book_details(page)
        if data:
            data['Author_Name'] = author_name
            data['GoodReads_Book_URL'] = link
            await page.close()
            return data
        await page.close()
    except Exception as e:
        print(f"      [Error] Scraping {link}: {e}", flush=True)
        try: await page.close()
        except: pass
    return None

def format_row(data):
    link = data.get('GoodReads_Series_URL')
    if not link or link == "N/A":
        link = data.get('GoodReads_Book_URL')
        
    synopsis = data.get('Description', 'N/A')
    genre = data.get('Genre', 'N/A')
    subgenre = identify_subgenre(synopsis, [genre])
    
    return {
        'Name of Series': data.get('Book_Title', 'N/A'),
        'Author Name': data.get('Author_Name', 'N/A'),
        'Publisher': data.get('Publisher', 'N/A'),
        'GoodReads series link': link,
        'Number of PRIMARY books in the series': data.get('Num_Primary_Books', '1'),
        'Rating (out of 5) of Primary Book 1': data.get('GoodReads_Rating', 'N/A'),
        'Ratings (#) of Primary Book 1': data.get('GoodReads_Rating_Count', 'N/A'),
        'Synopsis (if available)': synopsis,
        'Romantasy = Yes or No?': "Yes" if subgenre != "N/A" else "No",
        'Romantasy Sub-Genre of series': subgenre,
        'Name of agent': 'N/A'
    }

async def run_repair():
    if not os.path.exists(MASTER_FILE):
        print(f"Error: {MASTER_FILE} not found.", flush=True)
        return

    df = pd.read_excel(MASTER_FILE)
    
    # Track which rows are currently empty for our targets
    empty_rows = {}
    for author_name, config in TARGETS.items():
        mask = (df['Author Name'] == author_name) & (df['Name of Series'].isna())
        indices = df[mask].index.tolist()
        indices = [idx for idx in indices if config['start'] <= idx <= config['end']]
        empty_rows[author_name] = indices
        print(f"[Init] {author_name} has {len(indices)} empty rows in the target range.", flush=True)

    # Collect existing books to avoid duplicates (Normalized)
    existing_books = set()
    for book in df['Name of Series'].dropna():
        existing_books.add(normalize(book))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        print("[System] Performing Mandatory Login...", flush=True)
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()

        for author_name, config in TARGETS.items():
            print(f"\n[Target] Starting recovery for: {author_name}", flush=True)
            
            discovery_page = await context.new_page()
            all_live_links = await get_all_author_book_links(discovery_page, author_name, existing_books)
            await discovery_page.close()
            
            if not all_live_links:
                print(f"No unique books found for {author_name}.", flush=True)
                continue

            # Limit total books to fill the gaps + some extra for appending
            for link in all_live_links:
                target_idx = None
                if empty_rows[author_name]:
                    target_idx = empty_rows[author_name].pop(0)
                
                data = await scrape_book_details(context, scraper, link, author_name)
                if data:
                    formatted = format_row(data)
                    title = data.get('Book_Title', '')
                    norm_title = normalize(title)
                    
                    if norm_title in existing_books:
                        safe_title = title.encode('ascii', 'replace').decode('ascii')
                        print(f"    [Skip] {safe_title} already exists. Skipping.", flush=True)
                        if target_idx is not None:
                            empty_rows[author_name].insert(0, target_idx)
                        continue
                        
                    if target_idx is not None:
                        safe_title = title.encode('ascii', 'replace').decode('ascii')
                        print(f"    [Save] Filling row {target_idx + 1} with: {safe_title}", flush=True)
                        for col, val in formatted.items():
                            df.at[target_idx, col] = val
                    else:
                        safe_title = title.encode('ascii', 'replace').decode('ascii')
                        print(f"    [Append] Adding unique book: {safe_title}", flush=True)
                        new_row_df = pd.DataFrame([formatted])
                        df = pd.concat([df, new_row_df], ignore_index=True)
                    
                    existing_books.add(norm_title)
                    df.to_excel(MASTER_FILE, index=False)
                    print(f"      [OK] Saved to Excel.", flush=True)
                
                # Dynamic delay to avoid rate limits during aggressive run
                await asyncio.sleep(random.uniform(3, 6))

        await browser.close()
        print("\nRepair Mission Complete!", flush=True)

if __name__ == "__main__":
    asyncio.run(run_repair())
