import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\deborah_harris_merged.xlsx"
MAX_CONCURRENT = 5

async def process_author(context, scraper, author, semaphore, results_list):
    async with semaphore:
        safe_author = str(author).encode('ascii', 'ignore').decode('ascii')
        print(f"Scraping top 2 books for author: '{safe_author}'...")
        
        page = await context.new_page()
        try:
            # 1. Search for the author and get the first 2 books
            books = await scraper.search_author_books_with_links(page, author, max_books=2)
            await page.close()

            if not books:
                print(f"[{safe_author}] No books found.")
                return

            print(f"[{safe_author}] Found {len(books)} books. Scraping details...")
            
            # 2. Scrape details for each of those 2 books
            for b in books:
                title = b.get('title', 'Unknown')
                link = b.get('link', 'N/A')
                safe_title = str(title).encode('ascii', 'ignore').decode('ascii')
                
                try:
                    data = await scraper.scrape_goodreads_data(context, title, author, existing_url=link)
                    if data:
                        new_row = {}
                        new_row['Author Name'] = author
                        new_row['Name of Series'] = data.get('Book_Title', title)
                        
                        s_link = data.get('GoodReads_Series_URL')
                        if not s_link or s_link == 'N/A':
                            s_link = data.get('GoodReads_Book_URL', 'N/A')
                        if s_link == 'N/A': s_link = ''
                        new_row['GoodReads series link'] = s_link
                        
                        new_row['Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                        
                        rating = data.get('Book1_Rating', 'N/A')
                        if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                        new_row['Rating (out of 5) of Primary Book 1'] = rating
                        
                        count = data.get('Book1_Num_Ratings', 'N/A')
                        if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                        new_row['Ratings (#) of Primary Book 1'] = count
                        
                        new_row['Synopsis (if available)'] = data.get('Description', 'N/A')
                        
                        # Add to our thread-safe list
                        results_list.append(new_row)
                        print(f"    [{safe_author}] Added '{safe_title}'.")
                    else:
                        print(f"    [{safe_author}] Details failed for '{safe_title}'.")
                except Exception as e:
                    print(f"    [{safe_author}] Error scraping book '{safe_title}': {e}")
                    
        except Exception as e:
            print(f"[{safe_author}] Error searching author: {e}")
            try:
                await page.close()
            except:
                pass


async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
            
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna("").astype(str)

    # Get unique authors
    if 'Author Name' not in df.columns:
        print("Error: 'Author Name' column missing.")
        return
        
    unique_authors = df['Author Name'].unique()
    valid_authors = [a.strip() for a in unique_authors if a and str(a).strip() and str(a).lower() != 'nan']

    print(f"Found {len(valid_authors)} unique authors to scrape.")

    tasks = []
    scraper = GoodreadsScraper(headless=False)
    results_list = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        for author in valid_authors:
            tasks.append(process_author(context, scraper, author, semaphore, results_list))
            
        print(f"Starting {len(tasks)} author scrape tasks concurrently...")
        await asyncio.gather(*tasks)
        
        await login_page.close()
        await browser.close()
        
    if results_list:
        print(f"--- Appending {len(results_list)} new books to Excel ---")
        new_df = pd.DataFrame(results_list)
        
        # Ensure all columns exist in the new df so concat is clean
        for col in df.columns:
            if col not in new_df.columns:
                new_df[col] = ""
                
        # Only keep columns that are in the original df to avoid schema bloat
        new_df = new_df[df.columns]
        
        df = pd.concat([df, new_df], ignore_index=True)
        
        # Drop duplicates where the Series name and Author are the exact same
        df = df.drop_duplicates(subset=['Name of Series', 'Author Name'])
        
        df.to_excel(EXCEL_FILE, index=False)
        print("Opening Excel file...")
        try:
            from style_books_authors import apply_styling
            apply_styling(EXCEL_FILE)
        except Exception as e:
            print(f"Could not apply styling: {e}")
            import subprocess
            subprocess.Popen(["start", EXCEL_FILE], shell=True)
    else:
        print("No new books were successfully scraped.")

    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
