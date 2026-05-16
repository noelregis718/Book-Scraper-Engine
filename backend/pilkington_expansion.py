import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os
import json
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

# Configuration
CATALOG_FILE = "Pilkington_Agency_Catalog_Final.xlsx"
CONCURRENCY_LIMIT = 5 # 5 tabs per author

async def scrape_book_data_task(context, scraper, link, author_name):
    """Task to scrape a single book page."""
    try:
        page = await context.new_page()
        await page.goto(link, timeout=60000)
        data = await scraper.extract_book_details(page) # Verify method name
        if data:
            data['GoodReads_Book_URL'] = link
            data['Author_Name'] = author_name
            await page.close()
            return data
        await page.close()
    except Exception as e:
        print(f"      [Error] Scraping {link}: {e}")
    return None

async def process_author_expansion(context, scraper, author_name):
    """Finds top 5 books and scrapes them all in parallel."""
    print(f"  [Mission] Expanding catalog for: {author_name}")
    try:
        search_page = await context.new_page()
        titles_and_links = await scraper.search_author_books_with_links(search_page, author_name, max_books=5)
        await search_page.close()
        
        if not titles_and_links:
            print(f"    [Skip] No books found for {author_name}.")
            return []

        print(f"    [Found] {len(titles_and_links)} books. Opening 5 tabs...")
        
        # Open 5 tabs together
        tasks = [scrape_book_data_task(context, scraper, item['link'], author_name) for item in titles_and_links]
        results = await asyncio.gather(*tasks)
        
        # Filter out failed scrapes
        return [r for r in results if r]
    except Exception as e:
        print(f"    [Error] Author {author_name}: {e}")
        return []

def format_row(data):
    """Converts scraped data into a catalog row dictionary."""
    # AGGRESSIVE LINK SAVING
    link = data.get('GoodReads_Series_URL')
    if not link or link == "N/A":
        link = data.get('GoodReads_Book_URL')
    
    # Classification
    synopsis = data.get('Description', 'N/A')
    genre = data.get('Genre', 'N/A')
    subgenre = identify_subgenre(synopsis, [genre])
    
    return {
        'Name of Series': data.get('Book_Title', 'N/A'),
        'Author Name': data.get('Author_Name', 'N/A'),
        'Publisher': 'Pilkington Agency', # Default
        'GoodReads series link': link,
        'Number of PRIMARY books in the series': data.get('Num_Primary_Books', '1'),
        'Rating (out of 5) of Primary Book 1': data.get('GoodReads_Rating', 'N/A'),
        'Ratings (#) of Primary Book 1': data.get('GoodReads_Rating_Count', 'N/A'),
        'Synopsis (if available)': synopsis,
        'Romantasy = Yes or No?': "Yes" if subgenre != "N/A" else "No",
        'Romantasy Sub-Genre of series': subgenre,
        'Name of agent': 'N/A'
    }

async def run_expansion_mission():
    # Load original authors
    source_df = pd.read_excel("authors_only.xlsx")
    author_list = source_df['Authors'].tolist()
    
    final_rows = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        # Login
        print("[System] Performing Mandatory Login...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()

        # Process each author (sequential authors, but parallel books)
        for author in author_list:
            books_data = await process_author_expansion(context, scraper, author)
            for book in books_data:
                final_rows.append(format_row(book))
            
            # Save partial progress after each author
            temp_df = pd.DataFrame(final_rows)
            temp_df.to_excel(CATALOG_FILE, index=False)
            print(f"    [Progress] Saved {len(final_rows)} total books so far.")

        await browser.close()
        print(f"\nExpansion Mission Complete! Total rows: {len(final_rows)}")
        os.startfile(CATALOG_FILE)

if __name__ == "__main__":
    asyncio.run(run_expansion_mission())
