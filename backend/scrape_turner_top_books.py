import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\Next_Agency.xlsx"
TRACKING_FILE = r"E:\Internship\PocketFM\backend\turner_authors_processed.txt"
MAX_CONCURRENT = 8  # Aggressive concurrency

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
            "Publisher": "Turner Publishing",
            "GoodReads series link": "",
            "Number of PRIMARY books in the series": 1,
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "No",
            "Romantasy Sub-Genre of series": "",
            "Name of agent in the main folder": "Turner Publishing"
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
    
    # Load tracked authors
    processed_authors = set()
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                processed_authors.add(line.strip())
                
    authors = df['Author Name'].dropna().unique()
    authors = [a for a in authors if str(a).strip() != '' and str(a).lower() != 'nan' and str(a) not in processed_authors]
    
    if not authors:
        print("All authors have been processed! No more authors left.")
        return
        
    print(f"Found {len(authors)} remaining authors. Launching aggressive Top Books scraping (Top 2 Highest Rated) for ALL of them!")
    
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
        
        print(f"--- Finding the top 2 highest rated books for {len(authors)} authors ---")
        for author in authors:
            safe_author = author.encode('ascii', 'ignore').decode('ascii')
            print(f"\nChecking author: {safe_author}")
            
            # Use scrape_top_books_by_author to ensure we get highest rated and count=2
            top_books = await scraper.scrape_top_books_by_author(context, author, count=2)
            
            if not top_books:
                print(f"  No books found on Goodreads for {safe_author}")
            else:
                existing_titles = df[df['Author Name'] == author]['Name of Series'].apply(normalize_title).tolist()
                
                for book in top_books:
                    # The return format from scrape_top_books_by_author is the full details dict!
                    # Wait, no. The user wants them appended directly. We can bypass process_new_book since scrape_top_books_by_author already did it!
                    found_title = book.get('Book_Title', '')
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
                        print(f"  [Queueing For Save] '{found_title.encode('ascii', 'ignore').decode('ascii')}'")
                        
                        row_data = {
                            "Name of Series": found_title,
                            "Author Name": author,
                            "Publisher": "Turner Publishing",
                            "Name of agent in the main folder": "Turner Publishing",
                            "GoodReads series link": book.get('GoodReads_Series_URL') if book.get('GoodReads_Series_URL') != 'N/A' else book.get('GoodReads_Book_URL', ''),
                            "Number of PRIMARY books in the series": book.get('Num_Primary_Books', 1),
                            "Rating (out of 5) of Primary Book 1": book.get('Book1_Rating') if book.get('Book1_Rating') != 'N/A' else book.get('GoodReads_Rating', 'N/A'),
                            "Ratings (#) of Primary Book 1": book.get('Book1_Num_Ratings') if book.get('Book1_Num_Ratings') != 'N/A' else book.get('GoodReads_Rating_Count', 'N/A'),
                            "Synopsis (if available)": book.get('Description', 'N/A'),
                            "Romantasy = Yes or No?": "No",
                            "Romantasy Sub-Genre of series": ""
                        }
                        new_books_to_scrape.append(row_data)
                        
            # Progressive save
            with open(TRACKING_FILE, 'a', encoding='utf-8') as f:
                f.write(author + '\n')
                
            if new_books_to_scrape:
                new_df = pd.DataFrame(new_books_to_scrape)
                new_df = new_df.reindex(columns=df.columns)
                df = pd.concat([df, new_df], ignore_index=True)
                df = df.drop_duplicates(subset=["Name of Series", "Author Name"], keep='first')
                df.to_excel(EXCEL_FILE, index=False)
                new_books_to_scrape.clear() # Clear queue after progressive save
        
        await login_page.close()
        await browser.close()
    
    print("\n--- Rebuilding Excel File with new data ---")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")

    print("\nALL DONE for this agency!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
