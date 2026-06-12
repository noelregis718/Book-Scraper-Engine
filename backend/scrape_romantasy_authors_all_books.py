import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"e:\Internship\PocketFM\romantasy_authors.xlsx"

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
    return str(t).lower().replace("&", "and").replace(" ", "")

async def get_all_author_books(page, author_name, max_books=50):
    try:
        print(f"    [Scraper] Searching for author: {author_name}...", flush=True)
        search_url = f"https://www.goodreads.com/search?q={author_name.replace(' ', '+')}"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2.5)
        
        author_link = await page.query_selector('a[href*="/author/show/"]')
        if not author_link:
            author_link = await page.query_selector('.authorName, .authorName__container a')

        if not author_link:
            print(f"    [Scraper] Could not find author profile for: {author_name}", flush=True)
            return []
            
        author_url = await author_link.evaluate("el => el.href")
        print(f"    [Scraper] Found author profile: {author_url}", flush=True)
        await page.goto(author_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2.5)
        
        # Scroll down to load more books if dynamic
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, window.innerHeight);")
            await asyncio.sleep(1)

        book_els = await page.query_selector_all('a.bookTitle, [data-testid="bookTitle"] a')
        results = []
        for el in book_els:
            title = (await el.inner_text()).strip()
            link = await el.evaluate("el => el.href")
            if link and link not in [r['link'] for r in results] and title:
                results.append({'title': title, 'link': link})
            if len(results) >= max_books:
                break
        
        return results
    except Exception as e:
        print(f"    [Scraper] Error getting books for author: {e}", flush=True)
        return []

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    existing_titles = [clean_title(t) for t in df['Name of Series'].dropna().tolist() if str(t).strip() and str(t).strip().upper() != 'AUTHORS']
    authors = df['Author Name'].dropna().unique().tolist()
    
    valid_authors = []
    for a in authors:
        a = str(a).strip()
        if a and a.lower() != 'nan' and a.upper() != 'AUTHORS':
            valid_authors.append(a)
            
    print(f"Found {len(valid_authors)} unique authors to scrape.")
    
    new_rows = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper()
        
        for author in valid_authors:
            print(f"\n======================================")
            print(f"AGGRESSIVE EXPANSION: Finding books for {author}...")
            
            page = await context.new_page()
            top_books = await get_all_author_books(page, author, max_books=50)
            await page.close()
            
            if not top_books:
                print(f"No books found for {author}. Skipping.")
                continue
                
            print(f"Found {len(top_books)} books for {author}. Extracting full details...")
            
            for book_data in top_books:
                book_title = book_data['title']
                book_link = book_data['link']
                
                if clean_title(book_title) in existing_titles:
                    print(f"Skipping duplicate: {book_title}")
                    continue
                    
                print(f"\n  -> Extracting details for: {book_title}")
                details = await scraper.scrape_goodreads_data(context, book_title, author, existing_url=book_link)
                
                if details:
                    new_row = pd.Series(index=ELEVEN_COLUMN_HEADERS, dtype=object)
                    new_row['Name of Series'] = details.get("Book_Title", book_title)
                    new_row['Author Name'] = details.get("Author_Found", author)
                    new_row['Publisher'] = ""
                    
                    if details.get("GoodReads_Series_URL", "N/A") != "N/A":
                        new_row['GoodReads series link'] = details["GoodReads_Series_URL"]
                    elif details.get("GoodReads_Book_URL", "N/A") != "N/A":
                        new_row['GoodReads series link'] = details["GoodReads_Book_URL"]
                    else:
                        new_row['GoodReads series link'] = ""
                        
                    if details.get("Book1_Rating", "N/A") != "N/A":
                        new_row['Rating (out of 5) of Primary Book 1'] = details["Book1_Rating"]
                    else:
                        new_row['Rating (out of 5) of Primary Book 1'] = details.get("GoodReads_Rating", "N/A")
                        
                    if details.get("Book1_Num_Ratings", "N/A") != "N/A":
                        new_row['Ratings (#) of Primary Book 1'] = details["Book1_Num_Ratings"]
                    else:
                        new_row['Ratings (#) of Primary Book 1'] = details.get("GoodReads_Rating_Count", "N/A")
                        
                    new_row['Number of PRIMARY books in the series'] = details.get("Num_Primary_Books", "1")
                    new_row['Synopsis (if available)'] = details.get("Description", "")
                    
                    new_row['Romantasy = Yes or No?'] = ""
                    new_row['Romantasy Sub-Genre of series'] = ""
                    new_row['Name of agent'] = ""
                    
                    new_rows.append(new_row)
                    existing_titles.append(clean_title(book_title))
                    print(f"  -> Added {book_title} to queue.")
                    
        await browser.close()
        
    if new_rows:
        print(f"\nScraping Complete! Appending {len(new_rows)} new books to {EXCEL_FILE}...")
        new_df = pd.DataFrame(new_rows, columns=ELEVEN_COLUMN_HEADERS)
        combined_df = pd.concat([df, new_df], ignore_index=True)
        # Sort by author name
        combined_df = combined_df.sort_values(by=['Author Name', 'Name of Series'], na_position='last')
        combined_df.to_excel(EXCEL_FILE, index=False)
        print("Done!")
    else:
        print("No new books were found to add.")

if __name__ == '__main__':
    asyncio.run(main())
