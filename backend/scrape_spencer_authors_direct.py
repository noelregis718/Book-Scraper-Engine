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

async def process_single_book(context, scraper, author, book_data, existing_titles):
    title = book_data['title']
    url = book_data['link']
    
    if clean_title(title) in existing_titles:
        print(f"[{author}] Skipping duplicate: {title}")
        return None
        
    print(f"[{author}] Opening direct tab for: {title}")
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        
        # Check for CAPTCHA on the book page
        if await page.query_selector('#captcha-image, .captcha'):
            print(f"\n[!!! ACTION REQUIRED !!!] CAPTCHA detected for '{title}'! Please solve it in the browser window.")
            await page.wait_for_selector('.BookPageMetadataSection__genre, .RatingStatistics__rating, [data-testid="description"]', timeout=300000)
            
        details = await scraper.extract_book_details(page)
        
        if details:
            new_row = pd.Series(index=ELEVEN_COLUMN_HEADERS, dtype=object)
            new_row['Name of Series'] = details.get("Book_Title", title)
            new_row['Author Name'] = author
            new_row['Publisher'] = "Spencer Hill Press"
            
            if details.get("GoodReads_Series_URL", "N/A") != "N/A":
                new_row['GoodReads series link'] = details["GoodReads_Series_URL"]
            else:
                new_row['GoodReads series link'] = url
                
            new_row['Rating (out of 5) of Primary Book 1'] = details.get("Book1_Rating", details.get("GoodReads_Rating", "N/A"))
            new_row['Ratings (#) of Primary Book 1'] = details.get("Book1_Num_Ratings", details.get("GoodReads_Rating_Count", "N/A"))
            new_row['Number of PRIMARY books in the series'] = details.get("Num_Primary_Books", "1")
            new_row['Synopsis (if available)'] = details.get("Description", "N/A")
            
            new_row['Romantasy = Yes or No?'] = "N/A"
            new_row['Romantasy Sub-Genre of series'] = "N/A"
            new_row['Name of agent'] = "N/A"
            
            return new_row
    except Exception as e:
        print(f"[{author}] Error extracting {title}: {e}")
    finally:
        await page.close()
    return None

async def process_author(author_semaphore, scraper, context, author, existing_titles):
    async with author_semaphore:
        print(f"[{author}] Searching author page for top 3 books...")
        page = await context.new_page()
        try:
            results = await scraper.search_author_books_with_links(page, author, max_books=3)
        except Exception as e:
            print(f"[{author}] Error finding author books: {e}")
            results = []
        finally:
            await page.close()
            
        if not results:
            print(f"[{author}] No books found.")
            return []
            
        print(f"[{author}] Found top 3 links: {[r['title'] for r in results]}")
        
        # Concurrently process the 3 books for this author directly from the grabbed links
        book_tasks = []
        for res in results:
            book_tasks.append(process_single_book(context, scraper, author, res, existing_titles))
            
        book_results = await asyncio.gather(*book_tasks)
        
        new_rows = []
        for r in book_results:
            if r is not None:
                new_rows.append(r)
                existing_titles.add(clean_title(r['Name of Series']))
        
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
        
        # Exactly 2 authors concurrently
        author_semaphore = asyncio.Semaphore(2)
        
        tasks = []
        for author in valid_authors:
            tasks.append(process_author(author_semaphore, scraper, context, author, existing_titles))
            
        print(f"Launching direct scraper: 2 authors * 3 book tabs = exactly 6 book tabs concurrently!")
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
