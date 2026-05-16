import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os
import json
import random
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

# Configuration
SOURCE_FILE = "1852_literary_authors.xlsx"
OUTPUT_FILE = "Deep_Catalog_Enrichment.xlsx"
CONCURRENCY_LIMIT = 10 

async def get_all_author_book_links(page, author_name):
    """Navigates through all pages of an author's books to collect ALL links."""
    print(f"  [Discovery] Finding full catalog for: {author_name}")
    try:
        # Humanized Search Interaction
        print("    [Stealth] Navigating to front page...")
        await page.goto("https://www.goodreads.com/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(random.uniform(2.0, 4.0))
        
        search_input = await page.query_selector('input[name="q"], input[name="query"], .searchBox__input')
        if search_input:
            print(f"    [Stealth] Typing author name: {author_name}...")
            await search_input.fill(author_name)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await search_input.press('Enter')
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except:
                await asyncio.sleep(5) # Fallback wait
        else:
            # Fallback if search bar isn't found
            search_url = f"https://www.goodreads.com/search?q={author_name.replace(' ', '+')}"
            await page.goto(search_url, wait_until="networkidle", timeout=60000)
            
        await asyncio.sleep(random.uniform(3.0, 5.0))
        
        # Robust Author Link Detection
        author_link = await page.query_selector('a[href*="/author/show/"]')
        if not author_link:
            author_link = await page.query_selector('.authorName, .authorName__container a, [data-testid="authorName"] a')
            
        if not author_link:
            # Try a second search with "author" keyword
            print(f"    [Retry] Searching with 'author' keyword for {author_name}...")
            await page.goto(f"https://www.goodreads.com/search?q={author_name.replace(' ', '+')}+author", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(4)
            author_link = await page.query_selector('a[href*="/author/show/"], .authorName')

        if not author_link:
            print(f"    [Error] Could not find author profile for {author_name}")
            return []
            
        author_url = await author_link.evaluate("el => el.href")
        
        # Go to "More books" page
        all_books_url = author_url.replace("/show/", "/list/")
        if "?" in all_books_url:
            all_books_url = all_books_url.split("?")[0]
            
        all_links = []
        current_page = 1
        
        while True:
            print(f"    [Pagination] Scraping Page {current_page}...")
            await page.goto(f"{all_books_url}?page={current_page}", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)
            
            book_els = await page.query_selector_all('a.bookTitle, [data-testid="bookTitle"] a')
            page_links = []
            for el in book_els:
                link = await el.evaluate("el => el.href")
                if link and link not in all_links:
                    page_links.append(link)
            
            if not page_links:
                break
                
            all_links.extend(page_links)
            
            # Check for "Next" button
            next_btn = await page.query_selector('a.next_page')
            if not next_btn:
                break
            current_page += 1
            
        print(f"    [Discovery Complete] Found {len(all_links)} total books for {author_name}.")
        return all_links
    except Exception as e:
        print(f"    [Error] Discovery failed for {author_name}: {e}")
        return []

async def scrape_book_task(context, scraper, link, author_name):
    try:
        page = await context.new_page()
        await page.goto(link, timeout=60000)
        data = await scraper.extract_book_details(page)
        if data:
            data['Author_Name'] = author_name
            data['GoodReads_Book_URL'] = link
            await page.close()
            return data
        await page.close()
    except Exception as e:
        print(f"      [Error] Scraping {link}: {e}")
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
        'Publisher': 'N/A',
        'GoodReads series link': link,
        'Number of PRIMARY books in the series': data.get('Num_Primary_Books', '1'),
        'Rating (out of 5) of Primary Book 1': data.get('GoodReads_Rating', 'N/A'),
        'Ratings (#) of Primary Book 1': data.get('GoodReads_Rating_Count', 'N/A'),
        'Synopsis (if available)': synopsis,
        'Romantasy = Yes or No?': "Yes" if subgenre != "N/A" else "No",
        'Romantasy Sub-Genre of series': subgenre,
        'Name of agent': 'N/A'
    }

async def run_deep_scrape():
    df_source = pd.read_excel(SOURCE_FILE)
    # PROCESS FINAL 4 AUTHORS (Indices 28-31)
    author_list = df_source.iloc[28:32, 0].tolist() 
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        # Login
        print("[System] Performing Mandatory Login...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()

        # Load existing data if it exists
        if os.path.exists(OUTPUT_FILE):
            final_df = pd.read_excel(OUTPUT_FILE)
            final_rows = final_df.to_dict('records')
        else:
            final_rows = []

        for author_name in author_list:
            # 1. Discover all links
            discovery_page = await context.new_page()
            all_links = await get_all_author_book_links(discovery_page, author_name)
            await discovery_page.close()
            
            if not all_links:
                print(f"No books found for {author_name}. Skipping.")
                continue

            # 2. Batch Scrape (10 at a time)
            print(f"[System] Starting Deep Scrape of {len(all_links)} books for {author_name}...")
            
            for i in range(0, len(all_links), CONCURRENCY_LIMIT):
                batch = all_links[i:i+CONCURRENCY_LIMIT]
                tasks = [scrape_book_task(context, scraper, link, author_name) for link in batch]
                results = await asyncio.gather(*tasks)
                for res in results:
                    if res:
                        final_rows.append(format_row(res))
                
                print(f"  [Progress] {author_name}: Scraped {len(final_rows)} total books so far...")

            # Save to Excel after each author
            pd.DataFrame(final_rows).to_excel(OUTPUT_FILE, index=False)
            print(f"  [Save] Catalog updated with {author_name}'s library.")

        await browser.close()
        print(f"\nDeep Scrape Complete! Total catalog size: {len(final_rows)} books.")
        os.startfile(OUTPUT_FILE)

if __name__ == "__main__":
    asyncio.run(run_deep_scrape())
