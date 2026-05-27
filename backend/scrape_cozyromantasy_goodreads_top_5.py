import asyncio
import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\CozyRomantasy_Merged.xlsx"

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

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    existing_titles = [clean_title(t) for t in df['Name of Series'].dropna().tolist() if str(t).strip() and str(t).strip().upper() != 'AUTHORS']
    authors = df['Author Name'].dropna().unique().tolist()
    
    # Clean up authors list (remove nans, blank)
    valid_authors = []
    for a in authors:
        a = str(a).strip()
        if a and a.lower() != 'nan' and a.upper() != 'AUTHORS':
            valid_authors.append(a)
            
    print(f"Found {len(valid_authors)} unique authors to aggressively scrape.")
    
    new_rows = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper()
        
        for author in valid_authors:
            print(f"\n======================================")
            print(f"AGGRESSIVE EXPANSION: Finding Top 5 books for {author}...")
            
            page = await context.new_page()
            top_books = await scraper.search_author_books(page, author, max_books=5)
            await page.close()
            
            if not top_books:
                print(f"No books found for {author}. Skipping.")
                continue
                
            print(f"Found {len(top_books)} books for {author}. Extracting full details...")
            
            for book_title in top_books:
                if clean_title(book_title) in existing_titles:
                    print(f"Skipping duplicate: {book_title}")
                    continue
                    
                print(f"\n  -> Extracting details for: {book_title}")
                details = await scraper.scrape_goodreads_data(context, book_title, author)
                
                if details:
                    # Append new row
                    new_row = pd.Series(index=ELEVEN_COLUMN_HEADERS, dtype=object)
                    new_row['Name of Series'] = details.get("Book_Title", book_title)
                    new_row['Author Name'] = details.get("Author_Found", author)
                    new_row['Publisher'] = "Cozy Coven"
                    
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
        print(f"\nPhase 2 Complete! Appending {len(new_rows)} new books to {EXCEL_FILE}...")
        new_df = pd.DataFrame(new_rows, columns=ELEVEN_COLUMN_HEADERS)
        combined_df = pd.concat([df, new_df], ignore_index=True)
        combined_df.to_excel(EXCEL_FILE, index=False)
        
        try:
            from apply_jra_style import apply_styling
            apply_styling(EXCEL_FILE)
        except:
            pass
            
        print("Running classification on the expanded sheet...")
        try:
            import classify_cozy_final
            classify_cozy_final.main()
        except Exception as e:
            print(f"Error classifying: {e}")
    else:
        print("No new books were found to add.")

if __name__ == '__main__':
    asyncio.run(main())
