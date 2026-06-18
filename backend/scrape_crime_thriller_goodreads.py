import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

# Import the existing aggressive GoodreadsScraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Crime_Thriller_Template.xlsx")

def extract_book_number_from_title(title):
    if not title or pd.isna(title):
        return ""
    # Looks for "#1", "Book 1", etc.
    match = re.search(r'(?:#|Book\s+)(\d+)', str(title), re.IGNORECASE)
    if match:
        return match.group(1)
    return ""

async def scrape_crime_thriller_goodreads():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)

    print("Launching Aggressive Goodreads Scraper...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
            geolocation={"longitude": -74.006, "latitude": 40.7128},
            permissions=["geolocation"]
        )
        scraper = GoodreadsScraper()

        for idx, row in df.iterrows():
            title = str(row.get('Title', '')).strip()
            author = str(row.get('Author', '')).strip()
            gr_link = str(row.get('Goodreads Link', '')).strip()
            gr_rating = str(row.get('Goodreads Rating', '')).strip()
            
            if not title or title.lower() == 'nan':
                continue

            # Skip if we already have the goodreads link and rating
            if gr_link != 'nan' and gr_link and 'goodreads.com' in gr_link and gr_rating != 'nan' and gr_rating:
                print(f"Skipping {title} by {author} - already has Goodreads data.")
                continue

            print(f"\nSearching Goodreads for: {title} by {author}")
            
            # Pass existing link if we have one to save search time
            existing_url = gr_link if ('goodreads.com' in gr_link) else "N/A"
            
            # Use the aggressive scrape method
            details = await scraper.scrape_goodreads_data(context, title, author, existing_url=existing_url)
            
            if details:
                # Map extracted details to Excel columns
                
                # 1. Goodreads Rating
                if details.get("GoodReads_Rating", "N/A") != "N/A":
                    df.at[idx, 'Goodreads Rating'] = details["GoodReads_Rating"]
                
                # 2. Goodreads No. of Ratings
                if details.get("GoodReads_Rating_Count", "N/A") != "N/A":
                    df.at[idx, 'Goodreads No. of Ratings'] = details["GoodReads_Rating_Count"]
                
                # 3. Series Link
                series_url = details.get("GoodReads_Series_URL", "N/A")
                if series_url != "N/A":
                    df.at[idx, 'Series Link'] = series_url
                    df.at[idx, 'Part of Series'] = "Yes"
                else:
                    # If it's a standalone
                    df.at[idx, 'Part of Series'] = "No"
                
                # 4. # of primary books
                if details.get("Num_Primary_Books", "1") != "N/A":
                    df.at[idx, '# of primary books'] = details["Num_Primary_Books"]
                
                # 5. Book Number (Extract from Book_Title)
                book_title_found = details.get("Book_Title", title)
                book_num = extract_book_number_from_title(book_title_found)
                if book_num:
                    df.at[idx, 'Book Number'] = book_num
                
                # 6. Goodreads Link
                if details.get("GoodReads_Book_URL", "N/A") != "N/A":
                    df.at[idx, 'Goodreads Link'] = details["GoodReads_Book_URL"]

            # Save incrementally to prevent data loss
            df.to_excel(EXCEL_FILE, index=False)
            
        await browser.close()
        
    print(f"\nScraping Complete! Final save to {EXCEL_FILE}...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("Applied styling successfully!")
    except Exception as e:
        print(f"Error applying style: {e}")

if __name__ == "__main__":
    asyncio.run(scrape_crime_thriller_goodreads())
