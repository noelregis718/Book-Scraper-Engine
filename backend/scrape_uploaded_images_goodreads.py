import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\books_from_uploaded_images.xlsx"

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    async with async_playwright() as p:
        # Launch browser headlessly as False so the user can see and solve CAPTCHAs if they appear
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper()
        
        for idx, row in df.iterrows():
            title = str(row.get('Name of Series', '')).strip()
            author = str(row.get('Author Name', '')).strip()
            existing_link = str(row.get('GoodReads series link', '')).strip()
            
            if not title or title.lower() == 'nan':
                continue
                
            # If we already have a valid link and a rating, we can skip, but since we want to be aggressive, 
            # let's only skip if we are absolutely sure we have the data.
            rating = str(row.get('Rating (out of 5) of Primary Book 1', '')).strip()
            if rating != 'nan' and rating and rating != 'N/A' and 'goodreads.com' in existing_link:
                print(f"Skipping '{title}' by '{author}' - already has details.")
                continue
                
            print(f"\n=======================================================")
            print(f"Searching Goodreads for: '{title}' by '{author}'")
            print(f"=======================================================")
            
            details = await scraper.scrape_goodreads_data(context, title, author)
            
            if details:
                # 1. GoodReads series link
                if details.get("GoodReads_Series_URL", "N/A") != "N/A":
                    df.at[idx, 'GoodReads series link'] = details["GoodReads_Series_URL"]
                elif details.get("GoodReads_Book_URL", "N/A") != "N/A":
                    df.at[idx, 'GoodReads series link'] = details["GoodReads_Book_URL"]
                    
                # 2. Rating (out of 5) of Primary Book 1
                if details.get("Book1_Rating", "N/A") != "N/A":
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details["Book1_Rating"]
                elif details.get("GoodReads_Rating", "N/A") != "N/A":
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details["GoodReads_Rating"]
                    
                # 3. Ratings (#) of Primary Book 1
                if details.get("Book1_Num_Ratings", "N/A") != "N/A":
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = details["Book1_Num_Ratings"]
                elif details.get("GoodReads_Rating_Count", "N/A") != "N/A":
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = details["GoodReads_Rating_Count"]
                    
                # 4. Number of PRIMARY books in the series
                if details.get("Num_Primary_Books", "1") != "N/A":
                    df.at[idx, 'Number of PRIMARY books in the series'] = details["Num_Primary_Books"]
                    
                # 5. Synopsis (if available)
                if details.get("Description", "N/A") != "N/A":
                    curr_syn = str(row.get('Synopsis (if available)', '')).strip()
                    if curr_syn.lower() == 'nan' or len(curr_syn) < 20:
                        df.at[idx, 'Synopsis (if available)'] = details["Description"]
                        
                # 6. Romantasy = Yes or No?
                if details.get("Romantasy_Subgenre", "No") != "No":
                    df.at[idx, 'Romantasy = Yes or No?'] = details["Romantasy_Subgenre"]
                    
                # 7. Romantasy Sub-Genre of series
                genre = details.get("Genre", "N/A")
                subgenre = details.get("Sub_Genre", "N/A")
                genre_str = ""
                if genre != "N/A":
                    genre_str += genre
                if subgenre != "N/A":
                    genre_str += f", {subgenre}" if genre_str else subgenre
                    
                if genre_str:
                    df.at[idx, 'Romantasy Sub-Genre of series'] = genre_str

            # Save incrementally after each book
            df.to_excel(EXCEL_FILE, index=False)
            
        await browser.close()
        
    print(f"\nPhase 1 Complete! Saving final {EXCEL_FILE}...")
    df.to_excel(EXCEL_FILE, index=False)
    
    # Try to reapply styling if format_excel_script is available
    try:
        sys.path.append(r"E:\Internship\PocketFM")
        import format_excel_script
    except Exception as e:
        print("Note: Styling script not automatically re-applied.")

if __name__ == '__main__':
    asyncio.run(main())
