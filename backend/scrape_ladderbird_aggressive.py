import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\ladderbird_books_scrape.xlsx"
MAX_CONCURRENT = 3

def normalize_title(title):
    if pd.isna(title) or not title:
        return ""
    t = str(title).lower()
    t = re.sub(r'[^\w\s]', '', t)
    return t.strip()

async def process_new_book(context, scraper, title, author, url, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii') if title else 'Unknown'
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        print(f"  [Scraping New Book] '{safe_title}' by {safe_author}...")
        
        row_data = {
            "Name of Series": title,
            "Author Name": author,
            "Publisher": "",
            "GoodReads series link": url,
            "Number of PRIMARY books in the series": "1",
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "No",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": "Ladderbird Agency"
        }
        
        try:
            data = await scraper.scrape_goodreads_data(context, title, author, existing_url=url)
            if data:
                link = data.get('GoodReads_Series_URL')
                if not link or link == 'N/A':
                    link = data.get('GoodReads_Book_URL', url)
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
            
        return row_data

async def run_scrape():
    df = pd.read_excel(EXCEL_FILE)
    
    # Get unique authors
    authors = df['Author Name'].dropna().unique()
    authors = [a for a in authors if str(a).strip() != '']
    print(f"Found {len(authors)} unique authors.")
    
    scraper = GoodreadsScraper()
    new_books_to_scrape = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        
        print("--- Finding up to 30 books for each author ---")
        for author in authors:
            safe_author = author.encode('ascii', 'ignore').decode('ascii')
            print(f"Checking author: {safe_author}")
            # Use login_page to just search the author with a high max_books
            top_books = await scraper.search_author_books_with_links(login_page, author, max_books=30)
            
            if not top_books:
                print(f"  No books found for {safe_author}")
                continue
                
            # Get existing normalized titles for this author
            existing_titles = df[df['Author Name'] == author]['Name of Series'].apply(normalize_title).tolist()
            
            for book in top_books:
                found_title = book['title']
                found_url = book['link']
                norm_found = normalize_title(found_title)
                
                exists = False
                for ex in existing_titles:
                    if not ex or not norm_found: continue
                    if ex in norm_found or norm_found in ex:
                        exists = True
                        break
                        
                if exists:
                    pass # Silently skip to not clutter output
                else:
                    print(f"  [Adding to Queue] '{found_title.encode('ascii', 'ignore').decode('ascii')}'")
                    new_books_to_scrape.append({'title': found_title, 'author': author, 'url': found_url})
                    # Add to existing so we don't add duplicates of duplicates
                    existing_titles.append(norm_found)
        
        await login_page.close()
        
        if not new_books_to_scrape:
            print("No new books to scrape. All books are already in the sheet!")
        else:
            print(f"--- Scraping {len(new_books_to_scrape)} new books aggressively ---")
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)
            tasks = []
            
            for b in new_books_to_scrape:
                tasks.append(process_new_book(context, scraper, b['title'], b['author'], b['url'], semaphore))
                
            new_rows = await asyncio.gather(*tasks)
            
            new_df = pd.DataFrame(new_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            
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
            cols = []
            for col in ELEVEN_COLUMN_HEADERS:
                if col in df.columns:
                    cols.append(col)
            for col in df.columns:
                if col not in cols:
                    cols.append(col)
            df = df[cols]
            
            print("--- Rebuilding Excel File with new data ---")
            df.to_excel(EXCEL_FILE, index=False)
            
        await browser.close()
    
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
