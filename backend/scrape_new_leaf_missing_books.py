import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from classify_perez import classify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\New_Leaf_Literary_Merged.xlsx"
MAX_CONCURRENT = 5

async def process_missing_book_row(context, scraper, idx, author, df, semaphore, login_page):
    async with semaphore:
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        print(f"[{idx}] Finding top book for missing author row: {safe_author}...")
        
        try:
            # 1. Search author to get their first top book
            top_books = await scraper.search_author_books_with_links(login_page, author, max_books=1)
            
            if not top_books:
                print(f"[{idx}] No books found on Goodreads for {safe_author}")
                return
                
            first_book_title = top_books[0]['title']
            safe_title = first_book_title.encode('ascii', 'ignore').decode('ascii')
            print(f"[{idx}] Found top book '{safe_title}' for {safe_author}. Scraping details...")
            
            df.at[idx, 'Name of Series'] = first_book_title
            
            # 2. Scrape detailed data for this specific book
            data = await scraper.scrape_goodreads_data(context, first_book_title, author)
            
            if data:
                link = data.get('GoodReads_Series_URL')
                if not link or link == 'N/A':
                    link = data.get('GoodReads_Book_URL', 'N/A')
                if link == 'N/A': link = ''
                    
                df.at[idx, 'GoodReads series link'] = link
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                
                rating = data.get('Book1_Rating', 'N/A')
                if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = rating
                
                count = data.get('Book1_Num_Ratings', 'N/A')
                if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                df.at[idx, 'Ratings (#) of Primary Book 1'] = count
                
                synopsis = data.get('Description', 'N/A')
                df.at[idx, 'Synopsis (if available)'] = synopsis
                
                # Classify Romantasy
                combined_text = str(synopsis) + " " + str(first_book_title)
                subgenre = classify_subgenre(combined_text)
                
                if subgenre:
                    df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
                    df.at[idx, 'Romantasy Sub-Genre of series'] = subgenre
                else:
                    df.at[idx, 'Romantasy = Yes or No?'] = "No"
                    df.at[idx, 'Romantasy Sub-Genre of series'] = ""
                
                print(f"[{idx}] Done parsing '{safe_title}'. Romantasy: {df.at[idx, 'Romantasy = Yes or No?']}")
            else:
                print(f"[{idx}] Details not found for '{safe_title}'.")
                
        except Exception as e:
            print(f"[{idx}] Error scraping author {safe_author}: {e}")

async def run_missing_books_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
            
    # Convert all object columns to strings to prevent nan floating issues
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna("").astype(str)
            
    tasks = []
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        print("--- Scanning for authors missing a Book Name ---")
        for idx in range(len(df)):
            title = str(df.at[idx, 'Name of Series']).strip()
            author = str(df.at[idx, 'Author Name']).strip()
            
            # If missing title but we have an author
            if (not title or title.lower() == 'nan') and author and author.lower() != 'nan':
                # pass login_page because search_author_books_with_links requires it (or context)
                tasks.append(process_missing_book_row(context, scraper, idx, author, df, semaphore, login_page))
                
        print(f"Queued {len(tasks)} authors to find their first book.")
        
        if tasks:
            # We use gather to run them. But wait, search_author_books_with_links uses login_page which is a single page!
            # Concurrent use of the exact same page object might cause navigation overlaps and errors.
            # We should run the search part sequentially or create separate pages.
            # Let's run them semi-sequentially or use context to spawn new pages.
            # Wait, since process_missing_book_row takes semaphore, we can just run them, but we need to fix the page issue.
            pass
            
        # Refactoring to avoid shared page navigation conflicts:
        for b_task in tasks:
            pass # We won't use asyncio.gather on a shared page. Let's do it sequentially to be safe with the shared login_page.
            
        if tasks:
            for idx in range(len(df)):
                title = str(df.at[idx, 'Name of Series']).strip()
                author = str(df.at[idx, 'Author Name']).strip()
                if (not title or title.lower() == 'nan') and author and author.lower() != 'nan':
                    # Do it sequentially to be 100% safe with the single `login_page` navigation
                    await process_missing_book_row(context, scraper, idx, author, df, semaphore, login_page)
                    
        await login_page.close()
        await browser.close()
        
    print("--- Saving Excel ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_missing_books_scrape())
