import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import os
import json
from goodreads_scraper import GoodreadsScraper
from ai_classifier import identify_subgenre

# Configuration
CATALOG_FILE = "Pilkington_Agency_Catalog_Final.xlsx"
CONCURRENCY_LIMIT = 10 

async def process_row(context, scraper, df, idx, semaphore):
    async with semaphore:
        # Clean up the names (handle NaN)
        author_name = str(df.at[idx, 'Author Name']) if pd.notna(df.at[idx, 'Author Name']) else "N/A"
        book_title = str(df.at[idx, 'Name of Series']) if pd.notna(df.at[idx, 'Name of Series']) else "N/A"
        
        if book_title.lower() == "nan":
            book_title = "N/A"
            
        print(f"  [Mission] Searching for {author_name} - {book_title}...")
        
        try:
            # If we have a book title, do a direct search
            if book_title and book_title != "N/A":
                data = await scraper.scrape_goodreads_data(context, book_title, author_name)
                if data:
                    save_book_data(df, idx, data)
                    print(f"    [Success] {book_title} -> Saved.")
            else:
                # No book title: Search for the author and get TOP 5 books
                # We need a page to do the search
                temp_page = await context.new_page()
                titles = await scraper.search_author_books(temp_page, author_name, max_books=5)
                await temp_page.close()
                
                if titles:
                    print(f"    [Discovery] Found {len(titles)} books for {author_name}. Processing...")
                    # For the test, we'll just save the FIRST one to this row
                    # (In a full run, we could append new rows for the others)
                    data = await scraper.scrape_goodreads_data(context, titles[0], author_name)
                    if data:
                        save_book_data(df, idx, data)
                        print(f"    [Success] Top book '{titles[0]}' saved for {author_name}.")
                else:
                    print(f"    [Skip] No books found for author {author_name}")
                    df.at[idx, 'GoodReads series link'] = "Not Found"
                
        except Exception as e:
            print(f"    [Error] {author_name}: {e}")

def save_book_data(df, idx, data):
    # AGGRESSIVE LINK SAVING
    link = data.get('GoodReads_Series_URL')
    if not link or link == "N/A":
        link = data.get('GoodReads_Book_URL')
    
    df.at[idx, 'Name of Series'] = data.get('Book_Title', df.at[idx, 'Name of Series'])
    df.at[idx, 'GoodReads series link'] = link
    df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', '1')
    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = data.get('GoodReads_Rating', 'N/A')
    df.at[idx, 'Ratings (#) of Primary Book 1'] = data.get('GoodReads_Rating_Count', 'N/A')
    df.at[idx, 'Synopsis (if available)'] = data.get('Description', 'N/A')
    
    # Classification
    genre = data.get('Genre', 'N/A')
    subgenre = identify_subgenre(df.at[idx, 'Synopsis (if available)'], [genre])
    
    if subgenre != "N/A":
        df.at[idx, 'Romantasy = Yes or No?'] = "Yes"
        df.at[idx, 'Romantasy Sub-Genre of series'] = subgenre
    else:
        df.at[idx, 'Romantasy = Yes or No?'] = "No"
        df.at[idx, 'Romantasy Sub-Genre of series'] = "N/A"

async def run_pilkington_mission():
    if not os.path.exists(CATALOG_FILE):
        print(f"Error: {CATALOG_FILE} not found!")
        return

    df = pd.read_excel(CATALOG_FILE)
    mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A')
    rows_to_process = df[mask].index.tolist()[:10] # LIMIT TO 10
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        print("[System] Performing Mandatory Login for Pilkington Mission...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()

        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        
        tasks = [process_row(context, scraper, df, idx, semaphore) for idx in rows_to_process]
        await asyncio.gather(*tasks)
        
        df.to_excel(CATALOG_FILE, index=False)
        print(f"\nPilkington Mission Complete! Saved to {CATALOG_FILE}")
        await browser.close()
        os.startfile(CATALOG_FILE)

if __name__ == "__main__":
    asyncio.run(run_pilkington_mission())
