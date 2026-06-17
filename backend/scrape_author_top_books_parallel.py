import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def process_author(author, existing_titles, scraper, context, sem, new_rows_list):
    async with sem:
        print(f"\n[Task Start] Processing Author: {author}")
        page = await context.new_page()
        try:
            # 1. Search author and get top books
            top_books = await scraper.search_author_books_with_links(page, author, max_books=3)
            
            if not top_books:
                print(f"  -> [{author}] Could not find books.")
                await page.close()
                return
                
            print(f"  -> [{author}] Found {len(top_books)} books. Extracting details...")
            
            for book in top_books:
                title = book['title']
                link = book['link']
                
                if title.lower().strip() in existing_titles:
                    print(f"  -> [{author}] Skipping '{title}' (already in Excel).")
                    continue
                    
                print(f"    - [{author}] Scraping details for: {title}")
                
                # Use existing scraper logic with the direct link
                data = await scraper.scrape_goodreads_data(context, title=title, author=author, existing_url=link)
                
                if data:
                    new_row = {
                        'Name of Series': title,
                        'Author Name': author,
                        'Publisher': 'Bookouture',
                        'GoodReads series link': data.get("GoodReads_Book_URL", link),
                        'Number of PRIMARY books in the series': data.get("Num_Primary_Books", "N/A"),
                        'Rating (out of 5) of Primary Book 1': data.get("Book1_Rating", "N/A"),
                        'Ratings (#) of Primary Book 1': data.get("Book1_Num_Ratings", "N/A"),
                        'Synopsis (if available)': data.get("Description", "N/A"),
                        'Romantasy = Yes or No?': "N/A",
                        'Romantasy Sub-Genre of series': data.get("Romantasy_Subgenre", "N/A"),
                        'Name of agent': "N/A"
                    }
                    new_rows_list.append(new_row)
                    existing_titles.add(title.lower().strip())
                    print(f"      [Success] Added '{title}' to queue.")
                else:
                    print(f"      [Failed] Could not extract details for '{title}'.")
                    
        except Exception as e:
            print(f"  -> [{author}] Error processing: {e}")
        finally:
            await page.close()

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format_2.xlsx')
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    
    authors = df['Author Name'].dropna().unique().tolist()
    authors = [a for a in authors if str(a).strip() not in ["", "N/A", "Unknown", "nan"]]
    
    print(f"Found {len(authors)} unique authors to scrape.")

    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Login sequentially first to establish session
        print("Logging into Goodreads...")
        await scraper.login_to_goodreads(page)
        await page.close()
        
        # We will append new books to this list
        new_rows = []
        existing_titles = set([str(t).lower().strip() for t in df['Name of Series'].dropna().tolist()])
        
        # Use a semaphore to limit to 5 tabs concurrently
        sem = asyncio.Semaphore(5)
        
        tasks = []
        for author in authors:
            tasks.append(process_author(author, existing_titles, scraper, context, sem, new_rows))
            
        print("\n--- Starting Parallel Scraping (5 Tabs at once) ---")
        await asyncio.gather(*tasks)
            
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
