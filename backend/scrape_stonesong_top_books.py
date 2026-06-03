import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\Stonesong_Books.xlsx"
MAX_CONCURRENT = 3

def normalize_title(title):
    if pd.isna(title) or not title:
        return ""
    t = str(title).lower()
    t = re.sub(r'[^\w\s]', '', t)
    return t.strip()

async def process_new_book(context, scraper, title, author, semaphore, file_lock):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        print(f"  [Scraping New Book] '{safe_title}' by {safe_author}...")
        
        row_data = {
            "Name of Series": title,
            "Author Name": author,
            "Publisher": "",
            "GoodReads series link": "",
            "Number of PRIMARY books in the series": 1,
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "No",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": "Stonesong"
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
                
                row_data['Synopsis (if available)'] = data.get('Description', 'N/A')
                row_data['Romantasy = Yes or No?'] = data.get('Romantasy_Subgenre', 'No')
                row_data['Romantasy Sub-Genre of series'] = data.get('Genre', 'N/A')
                
                print(f"  [Done] '{safe_title}'")
            else:
                print(f"  [Not Found] '{safe_title}'")
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"  [Error] '{safe_title}': {err_msg}")
            
        # Immediate save logic as requested by user
        async with file_lock:
            try:
                df = pd.read_excel(EXCEL_FILE, keep_default_na=False)
                new_df = pd.DataFrame([row_data])
                df = pd.concat([df, new_df], ignore_index=True)
                df.to_excel(EXCEL_FILE, index=False)
                print(f"  [Saved immediately] '{safe_title}'")
            except Exception as e:
                print(f"  [Error Saving] '{safe_title}': {e}")
                
        return row_data

async def run_scrape():
    df = pd.read_excel(EXCEL_FILE, keep_default_na=False)
    
    # Get unique authors, ignoring 'Unknown' or empty
    authors = df['Author Name'].dropna().unique()
    authors = [a for a in authors if str(a).strip().lower() not in ['', 'nan', 'unknown', '[author name to be fetched]']]
    print(f"Found {len(authors)} unique known authors.")
    
    scraper = GoodreadsScraper(headless=False)
    new_books_to_scrape = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        login_page = await context.new_page()
        print("[System] Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        print("--- Finding top 2 books for each author ---")
        for author in authors:
            safe_author = author.encode('ascii', 'ignore').decode('ascii')
            print(f"Checking author: {safe_author}")
            # Get top 2 books
            top_books = await scraper.search_author_books_with_links(login_page, author, max_books=2)
            
            if not top_books:
                print(f"  No books found for {safe_author}")
                continue
                
            # Get existing normalized titles for this author
            existing_titles = df[df['Author Name'] == author]['Name of Series'].apply(normalize_title).tolist()
            
            for book in top_books:
                found_title = book['title']
                norm_found = normalize_title(found_title)
                
                # Check if it exists in current df
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
                    
        await login_page.close()
        
        if not new_books_to_scrape:
            print("No new books to scrape. All top 2 books are already in the sheet!")
        else:
            print(f"\n--- Scraping {len(new_books_to_scrape)} new books aggressively ---")
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)
            file_lock = asyncio.Lock()
            tasks = []
            
            for b in new_books_to_scrape:
                tasks.append(process_new_book(context, scraper, b['title'], b['author'], semaphore, file_lock))
                
            await asyncio.gather(*tasks)
            
        await browser.close()
    
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
