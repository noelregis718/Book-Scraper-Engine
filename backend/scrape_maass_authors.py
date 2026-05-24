import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\Maass_Agency_Complete_List_With_Image_Books.xlsx"
MAX_CONCURRENT = 5

ELEVEN_COLUMN_HEADERS = [
    "Name of Series",
    "Author Name",
    "Publisher",
    "GoodReads series link",
    "Number of PRIMARY books in the series",
    "Rating (out of 5) of Primary Book 1",
    "Ratings (#) of Primary Book 1",
    "Synopsis (if available)",
    "Romantasy = Yes or No?",
    "Romantasy Sub-Genre of series",
    "Name of agent",
]

async def process_author_books(context, scraper, author, existing_titles, semaphore):
    new_rows = []
    async with semaphore:
        safe_author = str(author).encode('ascii', 'ignore').decode('ascii')
        print(f"\n[Author Scraping] Looking up {safe_author}...")
        
        try:
            page = await context.new_page()
            books = await scraper.search_author_books_with_links(page, author, max_books=2)
            await page.close()
            
            if not books:
                print(f"  [Not Found] No books found for author {safe_author}")
                return []
                
            for book in books:
                title = book['title']
                link = book['link']
                safe_title = title.encode('ascii', 'ignore').decode('ascii')
                
                # Check if we already have it
                title_lower = str(title).lower().strip()
                if title_lower in existing_titles:
                    print(f"  [Skipping] '{safe_title}' already exists in excel for {safe_author}.")
                    continue
                    
                print(f"  [Scraping New Book] '{safe_title}' by {safe_author}...")
                data = await scraper.scrape_goodreads_data(context, title, author, existing_url=link)
                
                if data:
                    row = {header: "" for header in ELEVEN_COLUMN_HEADERS}
                    
                    row["Name of Series"] = title
                    row["Author Name"] = author
                    
                    # Links
                    found_link = data.get('GoodReads_Series_URL')
                    if not found_link or found_link == 'N/A':
                        found_link = data.get('GoodReads_Book_URL', 'N/A')
                    if found_link == 'N/A': found_link = ''
                    row["GoodReads series link"] = found_link
                    
                    row["Number of PRIMARY books in the series"] = data.get('Num_Primary_Books', 1)
                    
                    # Ratings
                    rating = data.get('Book1_Rating', 'N/A')
                    if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                    row["Rating (out of 5) of Primary Book 1"] = rating
                    
                    count = data.get('Book1_Num_Ratings', 'N/A')
                    if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                    row["Ratings (#) of Primary Book 1"] = count
                    
                    row["Synopsis (if available)"] = data.get('Description', 'N/A')
                    row["Romantasy = Yes or No?"] = data.get('Romantasy_Subgenre', 'No')
                    
                    new_rows.append(row)
                    print(f"  [Success] '{safe_title}' scraped successfully.")
                else:
                    print(f"  [Failed] Could not scrape data for '{safe_title}'")
                    
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"  [Error] {safe_author}: {err_msg}")
            
    return new_rows

async def run_scrape():
    df = pd.read_excel(EXCEL_FILE)
    
    # Ensure it's using the 11 column format
    for col in ELEVEN_COLUMN_HEADERS:
        if col not in df.columns:
            df[col] = ""
            
    # Get unique authors
    authors = df['Author Name'].dropna().unique()
    authors = [a for a in authors if str(a).strip().lower() not in ['nan', '']]
    
    # Map of existing titles to avoid duplicates (case insensitive)
    # We can use a set of lowercase titles
    existing_titles = set(str(t).lower().strip() for t in df['Name of Series'].dropna())
    
    tasks_to_run = []
    
    scraper = GoodreadsScraper()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        
        print(f"--- Processing {len(authors)} Unique Authors ---")
        for author in authors:
            tasks_to_run.append(process_author_books(context, scraper, author, existing_titles, semaphore))
        
        # Run all author tasks
        results = await asyncio.gather(*tasks_to_run)
        
        # Flatten the results
        new_rows = []
        for res in results:
            new_rows.extend(res)
            
        await browser.close()
        
    print(f"--- Found {len(new_rows)} New Books. Rebuilding Excel File ---")
    if new_rows:
        new_df = pd.DataFrame(new_rows, columns=ELEVEN_COLUMN_HEADERS)
        # Ensure we only have the 11 columns in df
        df = df[ELEVEN_COLUMN_HEADERS]
        final_df = pd.concat([df, new_df], ignore_index=True)
        final_df.to_excel(EXCEL_FILE, index=False)
        print("Excel file updated successfully.")
    else:
        print("No new books were added.")
        
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
