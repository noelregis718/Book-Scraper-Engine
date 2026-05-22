import asyncio
import json
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"e:\Internship\PocketFM\madeleine_milburn_combined.xlsx"
STATE_FILE = r"e:\Internship\PocketFM\backend\madeleine_state.json"
MAX_CONCURRENT = 5
BATCH_SIZE = 10

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

def rebuild_excel(df_original, state):
    final_rows = []
    for index, row in df_original.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        author = str(row.get('Author Name', '')).strip()
        
        # If the row has no title (i.e. row 107 onwards)
        if not title or title.lower() == 'nan':
            if author in state:
                books = state[author]
                if not books:
                    new_row = row.copy()
                    new_row['Name of Series'] = "N/A"
                    final_rows.append(new_row)
                else:
                    for b in books:
                        new_row = row.copy()
                        new_row['Name of Series'] = b.get('title', 'Unknown Title')
                        new_row['GoodReads series link'] = b.get('GoodReads_Series_URL') or b.get('GoodReads_Book_URL', 'N/A')
                        new_row['Number of PRIMARY books in the series'] = b.get('Num_Primary_Books', 1)
                        new_row['Rating (out of 5) of Primary Book 1'] = b.get('Book1_Rating', b.get('GoodReads_Rating', 'N/A'))
                        new_row['Ratings (#) of Primary Book 1'] = b.get('Book1_Num_Ratings', b.get('GoodReads_Rating_Count', 'N/A'))
                        new_row['Synopsis (if available)'] = b.get('Description', 'N/A')
                        new_row['Romantasy = Yes or No?'] = b.get('Romantasy_Subgenre', 'No')
                        new_row['Romantasy Sub-Genre of series'] = ""
                        new_row['Name of agent'] = "Madeleine Milburn"
                        new_row['Publisher'] = "Madeleine Milburn Literary Agency"
                        final_rows.append(new_row)
            else:
                # Not yet scraped
                final_rows.append(row)
        else:
            final_rows.append(row)
            
    # Save back to excel
    df_new = pd.DataFrame(final_rows)
    df_new.to_excel(EXCEL_FILE, index=False)
    
    # Re-apply styling
    try:
        from format_madwoman import format_madwoman
        format_madwoman(EXCEL_FILE, EXCEL_FILE)
        os.system(r'powershell -Command "Copy-Item e:\Internship\PocketFM\madeleine_milburn_combined.xlsx -Destination C:\Users\noelr\Downloads\madeleine_milburn_combined.xlsx -Force"')
    except Exception as e:
        print(f"[Warning] Could not reapply style: {e}")

async def process_author(context, scraper, author, semaphore):
    async with semaphore:
        safe_author = author.encode('ascii', 'ignore').decode('ascii')
        print(f"  [Scraping] {safe_author}...")
        try:
            # Search for their top 3 books
            page = await context.new_page()
            import re
            search_author = re.sub(r'[^\w\s]', '', author)
            book_links = await scraper.search_author_books_with_links(page, search_author, max_books=3)
            await page.close()
            
            books_data = []
            if not book_links:
                print(f"  [Not Found] No books for {safe_author}")
                return author, []
                
            for b in book_links:
                title = b.get('title')
                safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
                print(f"    -> Fetching details for '{safe_title}'")
                data = await scraper.scrape_goodreads_data(context, title, author)
                if data:
                    data['title'] = title
                    books_data.append(data)
                else:
                    books_data.append({'title': title})
            
            print(f"  [Done] {safe_author} ({len(books_data)} books)")
            return author, books_data
            
        except Exception as e:
            print(f"  [Error] {safe_author}: {str(e).encode('ascii', 'ignore').decode('ascii')}")
            return author, None

async def run_scrape():
    df = pd.read_excel(EXCEL_FILE)
    state = load_state()
    
    authors_to_scrape = []
    for index, row in df.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        author = str(row.get('Author Name', '')).strip()
        if (not title or title.lower() == 'nan') and author and author.lower() != 'nan':
            if author not in state:
                authors_to_scrape.append(author)
                
    if not authors_to_scrape:
        print("No new authors to scrape!")
        return
        
    print(f"Found {len(authors_to_scrape)} authors to scrape.")
    
    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Login first
        print("[System] Logging in to Goodreads...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        
        # Process in batches
        for i in range(0, len(authors_to_scrape), BATCH_SIZE):
            batch = authors_to_scrape[i:i+BATCH_SIZE]
            print(f"\n--- Processing Batch {i//BATCH_SIZE + 1} ({len(batch)} authors) ---")
            
            tasks = [process_author(context, scraper, author, semaphore) for author in batch]
            results = await asyncio.gather(*tasks)
            
            for author, books in results:
                if books is not None:
                    state[author] = books
                    
            save_state(state)
            print("--- Rebuilding Excel File with new data ---")
            rebuild_excel(df, state)
            
        await browser.close()
        print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
