import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\Spencer_Hill_Press.xlsx"

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
    "Name of agent"
]

def clean_title(t):
    return str(t).lower().replace("&", "and").replace(" ", "").strip()

async def process_author(semaphore, scraper, context, author, existing_titles):
    async with semaphore:
        print(f"[{author}] Searching for top 3 books...")
        page = await context.new_page()
        try:
            top_books = await scraper.search_author_books(page, author, max_books=3)
        except Exception as e:
            print(f"[{author}] Error finding books: {e}")
            top_books = []
        finally:
            await page.close()
            
        if not top_books:
            print(f"[{author}] No books found.")
            return []
            
        print(f"[{author}] Found top books: {top_books}")
        
        new_rows = []
        for book_title in top_books:
            if clean_title(book_title) in existing_titles:
                print(f"[{author}] Skipping duplicate: {book_title}")
                continue
                
            print(f"[{author}] Extracting details for: {book_title}")
            try:
                details = await scraper.scrape_goodreads_data(context, book_title, author)
            except Exception as e:
                print(f"[{author}] Error extracting {book_title}: {e}")
                continue
                
            if details:
                new_row = pd.Series(index=ELEVEN_COLUMN_HEADERS, dtype=object)
                new_row['Name of Series'] = details.get("Book_Title", book_title)
                new_row['Author Name'] = details.get("Author_Found", author)
                new_row['Publisher'] = "Spencer Hill Press"
                
                if details.get("GoodReads_Series_URL", "N/A") != "N/A":
                    new_row['GoodReads series link'] = details["GoodReads_Series_URL"]
                else:
                    new_row['GoodReads series link'] = details.get("GoodReads_Book_URL", "N/A")
                    
                new_row['Rating (out of 5) of Primary Book 1'] = details.get("Book1_Rating", details.get("GoodReads_Rating", "N/A"))
                new_row['Ratings (#) of Primary Book 1'] = details.get("Book1_Num_Ratings", details.get("GoodReads_Rating_Count", "N/A"))
                new_row['Number of PRIMARY books in the series'] = details.get("Num_Primary_Books", "1")
                new_row['Synopsis (if available)'] = details.get("Description", "N/A")
                
                new_row['Romantasy = Yes or No?'] = "N/A"
                new_row['Romantasy Sub-Genre of series'] = "N/A"
                new_row['Name of agent'] = "N/A"
                
                new_rows.append(new_row)
                existing_titles.add(clean_title(book_title))
                
        return new_rows

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    existing_titles = set(clean_title(t) for t in df['Name of Series'].dropna().tolist())
    authors = df['Author Name'].dropna().unique().tolist()
    
    valid_authors = []
    for a in authors:
        a = str(a).strip()
        if a and a.lower() not in ['nan', 'n/a']:
            valid_authors.append(a)
            
    print(f"Found {len(valid_authors)} unique authors.")
    
    all_new_rows = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        scraper = GoodreadsScraper()
        
        # Aggressive concurrency
        semaphore = asyncio.Semaphore(5)
        
        tasks = []
        for author in valid_authors:
            tasks.append(process_author(semaphore, scraper, context, author, existing_titles))
            
        print(f"Launching aggressive scraper for {len(valid_authors)} authors...")
        results = await asyncio.gather(*tasks)
        
        for res_list in results:
            if res_list:
                all_new_rows.extend(res_list)
                
        await browser.close()
        
    if all_new_rows:
        print(f"\nAppending {len(all_new_rows)} new books to {EXCEL_FILE}...")
        new_df = pd.DataFrame(all_new_rows, columns=ELEVEN_COLUMN_HEADERS)
        for col in df.columns:
            if col not in new_df.columns:
                new_df[col] = "N/A"
        combined_df = pd.concat([df, new_df], ignore_index=True)
        combined_df.to_excel(EXCEL_FILE, index=False)
        print("Done! All new books saved.")
    else:
        print("\nNo new books were found to add.")

if __name__ == '__main__':
    asyncio.run(main())
