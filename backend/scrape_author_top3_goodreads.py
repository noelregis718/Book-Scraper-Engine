import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format.xlsx')
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    
    # Get unique authors
    authors = df['Author Name'].dropna().unique().tolist()
    # Remove 'N/A', 'Unknown', or empty strings
    authors = [a for a in authors if str(a).strip() not in ["", "N/A", "Unknown", "nan"]]
    
    print(f"Found {len(authors)} unique authors to scrape.")

    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        await scraper.login_to_goodreads(page)
        
        # We will append new books to this list and convert to df to concat later
        new_rows = []
        
        # Track existing titles to avoid exact duplicates
        existing_titles = [str(t).lower().strip() for t in df['Name of Series'].dropna().tolist()]
        
        for idx, author in enumerate(authors):
            print(f"\n[{idx + 1}/{len(authors)}] Processing Author: {author}")
            
            try:
                # 1. Search author and get top 3 books
                top_books = await scraper.search_author_books_with_links(page, author, max_books=3)
                
                if not top_books:
                    print(f"  -> Could not find books for {author}.")
                    continue
                    
                print(f"  -> Found {len(top_books)} books for {author}. Extracting details...")
                
                for book in top_books:
                    title = book['title']
                    link = book['link']
                    
                    # Skip if already in excel
                    if title.lower().strip() in existing_titles:
                        print(f"  -> Skipping '{title}' (already in Excel).")
                        continue
                        
                    print(f"    - Scraping details for: {title}")
                    
                    # Use existing scraper logic with the direct link
                    data = await scraper.scrape_goodreads_data(context, title=title, author=author, existing_url=link)
                    
                    if data:
                        new_row = {
                            'Name of Series': title,
                            'Author Name': author,
                            'Publisher': 'Black Rose Writing',  # Assuming same publisher, or N/A
                            'GoodReads series link': data.get("GoodReads_Book_URL", link),
                            'Number of PRIMARY books in the series': data.get("Num_Primary_Books", "N/A"),
                            'Rating (out of 5) of Primary Book 1': data.get("Book1_Rating", "N/A"),
                            'Ratings (#) of Primary Book 1': data.get("Book1_Num_Ratings", "N/A"),
                            'Synopsis (if available)': data.get("Description", "N/A"),
                            'Romantasy = Yes or No?': "N/A",
                            'Romantasy Sub-Genre of series': data.get("Romantasy_Subgenre", "N/A"),
                            'Name of agent': "N/A"
                        }
                        new_rows.append(new_row)
                        existing_titles.append(title.lower().strip())
                        print(f"      [Success] Added '{title}' to queue.")
                    else:
                        print(f"      [Failed] Could not extract details for '{title}'.")
                        
            except Exception as e:
                print(f"  -> Error processing author {author}: {e}")
                
            # Auto-save every 2 authors
            if (idx + 1) % 2 == 0 and len(new_rows) > 0:
                temp_df = pd.DataFrame(new_rows)
                combined_df = pd.concat([df, temp_df], ignore_index=True)
                combined_df.to_excel(excel_path, index=False)
                print(f"  [Auto-Save] Progress saved. Total rows in Excel now: {len(combined_df)}")
                
        # Final save
        if len(new_rows) > 0:
            temp_df = pd.DataFrame(new_rows)
            combined_df = pd.concat([df, temp_df], ignore_index=True)
            combined_df.to_excel(excel_path, index=False)
            print(f"\n--- Scrape Complete! Added {len(new_rows)} new books. Total rows: {len(combined_df)} ---")
        else:
            print("\n--- Scrape Complete! No new books added. ---")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
