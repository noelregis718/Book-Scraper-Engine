import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from apply_jra_style import apply_styling

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'New_Agency.xlsx')
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    
    # Get unique authors from the first 17 rows (the initially added books)
    authors_df = df.head(17)
    authors = authors_df['Author Name'].dropna().unique().tolist()
    authors = [a for a in authors if str(a).strip() not in ["", "N/A", "Unknown", "nan"]]
    
    print(f"Found {len(authors)} unique authors to scrape.")

    scraper = GoodreadsScraper(headless=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        await scraper.login_to_goodreads(page)
        
        new_rows = []
        
        # Read the current excel to know what we have and prevent exact duplicates
        df = pd.read_excel(excel_path)
        existing_titles = [str(t).lower().strip() for t in df['Name of Series'].dropna().tolist()]
        
        for idx, author in enumerate(authors):
            print(f"\n[{idx + 1}/{len(authors)}] Processing Author: {author}")
            
            try:
                top_books = await scraper.search_author_books_with_links(page, author, max_books=3)
                
                if not top_books:
                    print(f"  -> Could not find books for {author}.")
                    continue
                    
                print(f"  -> Found {len(top_books)} books for {author}. Extracting details...")
                
                for book in top_books:
                    title = book['title']
                    link = book['link']
                    
                    if title.lower().strip() in existing_titles:
                        print(f"  -> Skipping '{title}' (already in Excel).")
                        continue
                        
                    print(f"    - Scraping details for: {title}")
                    
                    data = await scraper.scrape_goodreads_data(context, title=title, author=author, existing_url=link)
                    
                    if data:
                        new_row = {
                            'Name of Series': title,
                            'Author Name': author,
                            'Publisher': data.get("Publisher", "N/A"),
                            'GoodReads series link': data.get("GoodReads_Book_URL", link),
                            'Number of PRIMARY books in the series': data.get("Num_Primary_Books", "N/A"),
                            'Rating (out of 5) of Primary Book 1': data.get("Book1_Rating", "N/A"),
                            'Ratings (#) of Primary Book 1': data.get("Book1_Num_Ratings", "N/A"),
                            'Synopsis (if available)': data.get("Description", "N/A"),
                            'Romantasy = Yes or No?': "N/A",
                            'Romantasy Sub-Genre of series': data.get("Romantasy_Subgenre", "N/A"),
                            'Name of agent in the main folder': "N/A"
                        }
                        new_rows.append(new_row)
                        existing_titles.append(title.lower().strip())
                        print(f"      [Success] Added '{title}' to queue.")
                    else:
                        print(f"      [Failed] Could not extract details for '{title}'.")
                        
            except Exception as e:
                print(f"  -> Error processing author {author}: {e}")
                
            # Auto-save after each author is processed
            if len(new_rows) > 0:
                current_df = pd.read_excel(excel_path)
                temp_df = pd.DataFrame(new_rows)
                combined_df = pd.concat([current_df, temp_df], ignore_index=True)
                combined_df.to_excel(excel_path, index=False)
                new_rows = [] # reset new_rows after save
                
                # Re-apply styling
                try:
                    apply_styling(excel_path)
                except Exception as e:
                    print(f"Error styling: {e}")
                    
                print(f"  [Auto-Save] Progress saved. Total rows in Excel now: {len(combined_df)}")
                
        # Final save in case there are remaining rows
        if len(new_rows) > 0:
            current_df = pd.read_excel(excel_path)
            temp_df = pd.DataFrame(new_rows)
            combined_df = pd.concat([current_df, temp_df], ignore_index=True)
            combined_df.to_excel(excel_path, index=False)
            try:
                apply_styling(excel_path)
            except Exception as e:
                print(f"Error styling: {e}")
            print(f"\n--- Scrape Complete! Total rows: {len(combined_df)} ---")
        else:
            print("\n--- Scrape Complete! No new books to save at the end. ---")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
