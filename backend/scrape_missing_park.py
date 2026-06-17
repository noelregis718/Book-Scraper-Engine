import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import urllib.parse
import re

EXCEL_FILE = "e:/Internship/PocketFM/park_and_fine_books.xlsx"

async def scrape_book(context, df, index, title, author):
    page = await context.new_page()
    try:
        query = f"{title} {author}".strip()
        print(f"[{index}] Searching Goodreads directly for: {query}")
        
        search_url = f"https://www.goodreads.com/search?q={urllib.parse.quote_plus(query)}"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4)
        
        results = await page.query_selector_all('a.bookTitle')
        if not results:
            print(f"[{index}] No search results found on Goodreads for {query}")
            df.at[index, 'Rating (out of 5) of Primary Book 1'] = 0.0
            await page.close()
            return
            
        first_link = await results[0].get_attribute('href')
        full_link = "https://www.goodreads.com" + first_link if first_link.startswith('/') else first_link
        print(f"[{index}] Found book! Going to: {full_link}")
        await page.goto(full_link, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4)
            
        # We are now on the book page
        book_title_elem = await page.query_selector('h1[data-testid="bookTitle"]')
        book_title = await book_title_elem.inner_text() if book_title_elem else ""
        
        rating_elem = await page.query_selector('div.RatingStatistics__rating')
        rating = await rating_elem.inner_text() if rating_elem else ""
        
        ratings_count_elem = await page.query_selector('div.RatingStatistics__meta [data-testid="ratingsCount"]')
        ratings_count = await ratings_count_elem.inner_text() if ratings_count_elem else ""
        ratings_count = ratings_count.replace("ratings", "").replace(",", "").replace("rating", "").strip()
        
        synopsis_elem = await page.query_selector('div.DetailsLayoutRightParagraph__widthConstrained span.Formatted')
        if not synopsis_elem:
            synopsis_elem = await page.query_selector('div[data-testid="description"]')
        synopsis = await synopsis_elem.inner_text() if synopsis_elem else ""
        
        # Save the scraped book title if it was missing
        if not title and book_title:
            df.at[index, 'Name of Series'] = book_title
            
        df.at[index, 'GoodReads series link'] = page.url
        
        print(f"[{index}] Scraped Book: {book_title}, Rating: {rating}")
        
        # Safely convert to numeric types for Pandas
        try:
            rating_val = float(rating) if rating else None
        except:
            rating_val = None
            
        try:
            count_val = int(ratings_count) if ratings_count else None
        except:
            count_val = None
        
        df.at[index, 'Rating (out of 5) of Primary Book 1'] = rating_val
        df.at[index, 'Ratings (#) of Primary Book 1'] = count_val
        
        # Avoid charmap encoding issues when printing or saving synopsis
        df.at[index, 'Synopsis (if available)'] = str(synopsis)
                    
    except Exception as e:
        print(f"[{index}] Error scraping {query}: {e}")
        df.at[index, 'Rating (out of 5) of Primary Book 1'] = 0.0
        
    finally:
        await page.close()

async def main():
    df = pd.read_excel(EXCEL_FILE)
    
    # Ensure columns are object type so we can insert strings if needed
    for col in ['Name of Series', 'Synopsis (if available)', 'GoodReads series link', 'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1', 'Ratings (#) of Primary Book 1']:
        if col in df.columns and df[col].dtype != 'object':
            df[col] = df[col].astype('object')
            
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        tasks = []
        # The user requested rows 63 to 70 (indices 62 to 69 in pandas)
        for index in range(62, min(70, len(df))):
            title = "" if pd.isna(df.at[index, 'Name of Series']) else str(df.at[index, 'Name of Series']).strip()
            author = "" if pd.isna(df.at[index, 'Author Name']) else str(df.at[index, 'Author Name']).strip()
            tasks.append(scrape_book(context, df, index, title, author))
            
        print(f"Starting targeted batch of {len(tasks)} books...")
        await asyncio.gather(*tasks)
            
        df.to_excel(EXCEL_FILE, index=False)
        print("Targeted batch complete and saved to Excel!")
        
        await browser.close()

if __name__ == "__main__":
    # Fix console encoding to avoid charmap errors
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())
