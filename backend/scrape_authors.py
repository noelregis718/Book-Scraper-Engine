import asyncio
import pandas as pd
import urllib.parse
from playwright.async_api import async_playwright
import os
import json
import re

EXCEL_FILE = "e:/Internship/PocketFM/books_from_images.xlsx"
TRACKING_FILE = "e:/Internship/PocketFM/scraped_authors.json"

def load_scraped_authors():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    return []

def save_scraped_authors(authors):
    with open(TRACKING_FILE, "w") as f:
        json.dump(authors, f)

async def scrape_book_details(page, book_link, author):
    # Navigate to the book page
    print(f"[{author}] Navigating to book: {book_link}")
    await page.goto(book_link, wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(3)
    
    # Extract title
    title_elem = await page.query_selector('h1.Text__title1')
    title = await title_elem.inner_text() if title_elem else ""
    
    # Extract rating
    rating_elem = await page.query_selector('div.RatingStatistics__rating')
    rating = await rating_elem.inner_text() if rating_elem else ""
    
    # Extract count
    ratings_count_elem = await page.query_selector('div.RatingStatistics__meta [data-testid="ratingsCount"]')
    ratings_count = await ratings_count_elem.inner_text() if ratings_count_elem else ""
    ratings_count = ratings_count.replace("ratings", "").replace(",", "").replace("rating", "").strip()
    
    # Extract synopsis
    synopsis_elem = await page.query_selector('div.DetailsLayoutRightParagraph__widthConstrained span.Formatted')
    if not synopsis_elem:
        synopsis_elem = await page.query_selector('div[data-testid="description"]')
    synopsis = await synopsis_elem.inner_text() if synopsis_elem else ""
    
    series_link = ""
    num_primary_books = ""
    series_elem = await page.query_selector('h3.Text__h3 a')
    if series_elem:
        href = await series_elem.get_attribute('href')
        if href and "series" in href:
            series_link = href
    
    try:
        rating_val = float(rating) if rating else 0.0
    except:
        rating_val = 0.0
        
    try:
        count_val = int(ratings_count) if ratings_count else 0
    except:
        count_val = 0
        
    if series_link:
        full_series_link = series_link if series_link.startswith('http') else f"https://www.goodreads.com{series_link}"
        await page.goto(full_series_link, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
        series_desc_elem = await page.query_selector('div.responsiveSeriesHeader__subtitle')
        if series_desc_elem:
            desc = await series_desc_elem.inner_text()
            match = re.search(r'(\d+)\s+primary\s+works', desc, re.IGNORECASE)
            if match:
                num_primary_books = match.group(1)

    return {
        'Name of Series': title,
        'Author Name': author,
        'GoodReads series link': book_link,
        'Rating (out of 5) of Primary Book 1': rating_val,
        'Ratings (#) of Primary Book 1': count_val,
        'Synopsis (if available)': str(synopsis),
        'Number of PRIMARY books in the series': num_primary_books
    }

async def scrape_author(context, author):
    page = await context.new_page()
    new_books = []
    try:
        query = author.strip()
        print(f"[{author}] Searching Goodreads...")
        search_url = f"https://www.goodreads.com/search?q={urllib.parse.quote_plus(query)}"
        
        await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(3)
        
        # Click the first search result
        book_links = []
        results = await page.query_selector_all('a.bookTitle')
        
        if not results:
            print(f"[{author}] Trying DuckDuckGo fallback...")
            ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query + ' site:goodreads.com/book/show')}"
            await page.goto(ddg_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            ddg_links = await page.query_selector_all('a.result__url')
            
            for link in ddg_links[:3]:
                href = await link.get_attribute('href')
                if 'uddg=' in href:
                    actual_url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                    book_links.append(actual_url)
        else:
            for link in results[:3]:
                href = await link.get_attribute('href')
                full_link = "https://www.goodreads.com" + href if href.startswith('/') else href
                book_links.append(full_link)
        
        if not book_links:
            print(f"[{author}] No books found anywhere.")
            return []
            
        print(f"[{author}] Found {len(book_links)} books to scrape.")
        
        for book_link in book_links:
            try:
                book_data = await scrape_book_details(page, book_link, author)
                new_books.append(book_data)
            except Exception as e:
                print(f"[{author}] Error scraping book {book_link}: {e}")
                
        return new_books
                
    except Exception as e:
        print(f"[{author}] Error: {e}")
        return []
    finally:
        await page.close()


async def main():
    print("Loading excel file...")
    df = pd.read_excel(EXCEL_FILE)
    
    # We only want to extract the authors from the ORIGINAL rows. 
    # Since we will append new rows, we will track scraped authors
    scraped_authors = load_scraped_authors()
    
    all_authors = df['Author Name'].dropna().unique().tolist()
    authors_to_scrape = [a for a in all_authors if str(a).strip() != "" and a not in scraped_authors]
    
    print(f"Total authors to scrape: {len(authors_to_scrape)}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        batch_size = 6
        for i in range(0, len(authors_to_scrape), batch_size):
            batch = authors_to_scrape[i:i+batch_size]
            print(f"\n--- Starting new batch of {len(batch)} authors concurrently ---")
            
            tasks = []
            for author in batch:
                tasks.append(scrape_author(context, author))
                
            results = await asyncio.gather(*tasks)
            
            # results is a list of lists of dictionaries
            new_rows = []
            for res in results:
                new_rows.extend(res)
                
            if new_rows:
                new_df = pd.DataFrame(new_rows)
                # align columns
                for col in df.columns:
                    if col not in new_df.columns:
                        new_df[col] = pd.NA
                new_df = new_df[df.columns]
                
                # Append to original DF
                df = pd.concat([df, new_df], ignore_index=True)
                
                # Save
                df.to_excel(EXCEL_FILE, index=False)
                print(f"Appended {len(new_rows)} new books to Excel!")
                
            # Update tracking
            scraped_authors.extend(batch)
            save_scraped_authors(scraped_authors)
            print("Batch complete and saved!")
            
        await browser.close()
        print("No more authors to scrape!")

if __name__ == "__main__":
    asyncio.run(main())
