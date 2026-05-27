import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\D4EO_Merged.xlsx"
MAX_CONCURRENT = 5

def normalize_title(title):
    if pd.isna(title) or not title:
        return ""
    t = str(title).lower()
    t = re.sub(r'[^\w\s]', '', t)
    return t.strip()

async def process_new_book(context, scraper, title, author, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        print(f"  [Scraping New Book] '{safe_title}' by {safe_author}...")
        
        row_data = {
            "Name of Series": title,
            "Author Name": author,
            "Publisher": "D4EO Literary Agency",
            "GoodReads series link": "",
            "Number of PRIMARY books in the series": 1,
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "No",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": "Robert (Bob) G. Diforio"
        }
        
        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                link = data.get('GoodReads_Series_URL')
                if not link or link == 'N/A':
                    link = data.get('GoodReads_Book_URL', 'N/A')
                if link == 'N/A': link = ''
                    
                row_data['GoodReads series link'] = link
                row_data['Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                
                rating = data.get('Book1_Rating', 'N/A')
                if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                row_data['Rating (out of 5) of Primary Book 1'] = rating
                
                count = data.get('Book1_Num_Ratings', 'N/A')
                if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                row_data['Ratings (#) of Primary Book 1'] = count
                
                synopsis = data.get('Description', 'N/A')
                row_data['Synopsis (if available)'] = synopsis
                
                print(f"  [Done] Parsed details for '{safe_title}'")
            else:
                print(f"  [Not Found] Details for '{safe_title}'")
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"  [Error] '{safe_title}': {err_msg}")
            
        return row_data

async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return
        
    df = pd.read_excel(EXCEL_FILE)
    
    authors = df['Author Name'].dropna().unique()
    authors = [a for a in authors if str(a).strip() != '' and str(a).lower() != 'nan']
    print(f"Found {len(authors)} unique authors.")
    
    scraper = GoodreadsScraper(headless=False)
    new_books_to_scrape = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        print("--- Finding the top 3 books for each author to add if missing ---")
        for author in authors:
            safe_author = author.encode('ascii', 'ignore').decode('ascii')
            print(f"Checking author: {safe_author}")
            
            # Request up to 3 books
            top_books = await scraper.search_author_books_with_links(login_page, author, max_books=3)
            
            if not top_books:
                print(f"  No books found on Goodreads for {safe_author}")
                continue
                
            existing_titles = df[df['Author Name'] == author]['Name of Series'].apply(normalize_title).tolist()
            
            books_processed = 0
            for book in top_books:
                found_title = book['title']
                norm_found = normalize_title(found_title)
                
                exists = False
                for ex in existing_titles:
                    if not ex or not norm_found: continue
                    if ex in norm_found or norm_found in ex:
                        exists = True
                        break
                        
                if exists:
                    print(f"  [Skipping] '{found_title.encode('ascii', 'ignore').decode('ascii')}' - Already in sheet")
                else:
                    print(f"  [Adding to Queue] '{found_title.encode('ascii', 'ignore').decode('ascii')}'")
                    new_books_to_scrape.append({'title': found_title, 'author': author})
                    
                books_processed += 1
                if books_processed >= 3:
                    break
        
        await login_page.close()
        
        if not new_books_to_scrape:
            print("No new books to scrape. All top 3 books are already in the sheet!")
        else:
            print(f"--- Scraping details for {len(new_books_to_scrape)} new books ---")
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)
            tasks = []
            
            for b in new_books_to_scrape:
                tasks.append(process_new_book(context, scraper, b['title'], b['author'], semaphore))
                
            new_rows = await asyncio.gather(*tasks)
            
            new_df = pd.DataFrame(new_rows)
            # Make sure we use the 11 columns
            from merge_d4eo import ELEVEN_COLUMN_HEADERS
            new_df = new_df.reindex(columns=ELEVEN_COLUMN_HEADERS)
            
            df = pd.concat([df, new_df], ignore_index=True)
            
            # Deduplicate
            df = df.drop_duplicates(subset=["Name of Series", "Author Name"], keep='first')
            
            print("--- Rebuilding Excel File with new data ---")
            df.to_excel(EXCEL_FILE, index=False)
            
            try:
                from apply_jra_style import apply_styling
                apply_styling(EXCEL_FILE)
                print("--- Applied styling ---")
            except Exception as e:
                print(f"Could not apply styling: {e}")
                
        await browser.close()
    
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    
    if new_books_to_scrape:
        print("Re-running final subgenre mapping to ensure new synopses are classified...")
        try:
            import classify_d4eo_final
            classify_d4eo_final.main()
        except Exception as e:
            print(f"Failed to re-run mapping: {e}")
            
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
