import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def process_row(index, row, df, context, semaphore, excel_path, lock, scraper):
    title = str(row.get("Book 1 Title", "")).strip()
    author = str(row.get("Author Name", "")).strip()
    existing_rating = str(row.get("Book 1 Goodreads Rating", "")).strip()
    
    if not title or title.lower() == 'nan':
        return
        
    # Skip if we already scraped it
    if existing_rating and existing_rating.lower() != 'nan' and existing_rating != 'None':
        return

    async with semaphore:
        print(f"[{index+1}] Scraping: '{title}' by '{author}'", flush=True)
        try:
            # 1. Scrape standard data (Rating, URLs, Primary books) using the robust class
            data = await scraper.scrape_goodreads_data(context, title=title, author=author)
            
            if data:
                url_to_save = data.get("GoodReads_Series_URL", "N/A")
                if url_to_save == "N/A" or not url_to_save:
                    url_to_save = data.get("GoodReads_Book_URL", "")
                
                # 2. Extract page count by going directly to the Book URL
                book_url = data.get("GoodReads_Book_URL")
                num_pages = None
                
                if book_url and book_url != "N/A":
                    page = await context.new_page()
                    try:
                        await page.goto(book_url, wait_until="domcontentloaded", timeout=90000)
                        # Scroll to trigger lazy loading of page count elements
                        await page.evaluate("window.scrollBy(0, 1000)")
                        await asyncio.sleep(1)
                        await page.evaluate("window.scrollBy(0, 1000)")
                        await asyncio.sleep(1)
                        
                        content = await page.content()
                        soup = BeautifulSoup(content, 'html.parser')
                        text = soup.get_text(separator=' ')
                        
                        matches = re.findall(r'(\d+)\s*pages', text, re.IGNORECASE)
                        for m in matches:
                            if 10 < int(m) < 4000:
                                num_pages = m
                                break
                    except Exception as e:
                        print(f"  [{index+1}] Warning: Failed to extract pages for '{title}': {e}")
                    finally:
                        await page.close()

                # 3. Save to DataFrame safely
                async with lock:
                    df.at[index, "Goodreads Series URL"] = url_to_save
                    df.at[index, "Number of Primary Books"] = data.get("Num_Primary_Books", "")
                    
                    rating = data.get("Book1_Rating", "")
                    if rating and rating != "N/A":
                        df.at[index, "Book 1 Goodreads Rating"] = float(rating)
                        
                    ratings_count = data.get("Book1_Num_Ratings", "")
                    if ratings_count and ratings_count != "N/A":
                        # clean comma
                        clean_count = str(ratings_count).replace(",", "").split()[0]
                        if clean_count.isdigit():
                            df.at[index, "Number of Book 1 Ratings"] = int(clean_count)
                            
                    if num_pages:
                        df.at[index, "Number of Pages in Book 1"] = float(num_pages)
                        
                    df.to_excel(excel_path, index=False)
                
                print(f"  [{index+1}] Success for '{title}'. Pages: {num_pages if num_pages else 'N/A'}", flush=True)
            else:
                print(f"  [{index+1}] Failed to find book data for: '{title}'", flush=True)
        except Exception as e:
            print(f"  [{index+1}] Error for '{title}': {e}", flush=True)

async def run_scraper():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(workspace_dir, "Small_Mid_Sized_Publishers_Crime_Series_Expanded_30_Per_Publisher.xlsx")
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    df = pd.read_excel(input_path)
    
    # Fix pandas incompatible dtype issue when assigning strings/floats to NaN
    for col in ["Goodreads Series URL", "Number of Primary Books", "Book 1 Goodreads Rating", "Number of Book 1 Ratings", "Number of Pages in Book 1"]:
        if col in df.columns:
            df[col] = df[col].astype(object)
    
    # The user explicitly requested 8 tabs at once
    semaphore = asyncio.Semaphore(8)
    lock = asyncio.Lock()
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Login first so we have cookies for all 8 tabs
        page = await context.new_page()
        await scraper.login_to_goodreads(page)
        await page.close()
        
        tasks = []
        for index, row in df.iterrows():
            tasks.append(process_row(index, row, df, context, semaphore, input_path, lock, scraper))
            
        print(f"\nStarting 8 concurrent tabs to aggressively scrape {len(df)} books...", flush=True)
        await asyncio.gather(*tasks)
        
        await browser.close()
        
    print("\nScraping complete. Final dataset saved.", flush=True)

if __name__ == "__main__":
    asyncio.run(run_scraper())
