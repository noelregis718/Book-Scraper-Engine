import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\New_Romantasy_Books.xlsx"

async def scrape_author_top_books(context, author_name):
    page = await context.new_page()
    results = []
    try:
        print(f"  Searching Goodreads for author: {author_name}...", flush=True)
        search_url = f"https://www.goodreads.com/search?q={author_name.replace(' ', '+')}"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
        # Click the author link
        author_link = await page.query_selector('a[href*="/author/show/"]')
        if not author_link:
            author_link = await page.query_selector('.authorName, .authorName__container a')

        if not author_link:
            print(f"    Could not find author profile for: {author_name}", flush=True)
            await page.close()
            return []
            
        author_url = await author_link.evaluate("el => el.href")
        await page.goto(author_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
        # Wait for the book list
        await page.wait_for_selector('tr[itemtype="http://schema.org/Book"]', timeout=10000)
        
        # Goodreads author pages list books sorted by popularity by default
        book_rows = await page.query_selector_all('tr[itemtype="http://schema.org/Book"]')
        
        for row in book_rows[:2]: # Get first 2 books
            try:
                title_el = await row.query_selector('a.bookTitle span')
                title = (await title_el.inner_text()).strip() if title_el else "Unknown"
                
                link_el = await row.query_selector('a.bookTitle')
                link = await link_el.evaluate("el => el.href") if link_el else ""
                
                # Extract rating and number of ratings
                # E.g., " 4.39 avg rating — 12,345 ratings"
                meta_el = await row.query_selector('.minirating')
                meta_text = (await meta_el.inner_text()).strip() if meta_el else ""
                
                rating = ""
                ratings_count = ""
                
                if meta_text:
                    rating_match = re.search(r'([\d.]+)\s*avg rating', meta_text)
                    if rating_match:
                        rating = rating_match.group(1)
                        
                    count_match = re.search(r'—\s*([\d,]+)\s*rating', meta_text)
                    if count_match:
                        ratings_count = count_match.group(1).replace(',', '')
                
                results.append({
                    'title': title,
                    'link': link,
                    'rating': rating,
                    'ratings_count': ratings_count
                })
            except Exception as e:
                print(f"    Error extracting a book for {author_name}: {e}")
                
    except Exception as e:
        print(f"    Error processing author {author_name}: {e}")
    finally:
        await page.close()
        
    return results

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Get unique authors who actually have a name
    authors = df['Author Name'].dropna().unique()
    authors = [a for a in authors if str(a).strip() != "" and str(a).strip().lower() != "nan"]
    
    # Get existing book titles to avoid duplicates
    existing_titles = set(str(t).lower().strip() for t in df['Name of Series'].dropna())
    
    new_rows = []
    
    async with async_playwright() as p:
        # Running visible so you can solve CAPTCHAs if needed
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        for idx, author in enumerate(authors):
            print(f"\n[{idx+1}/{len(authors)}] Processing Author: {author}")
            books = await scrape_author_top_books(context, author)
            
            for book in books:
                print(f"    Found Book: {book['title']} (Rating: {book['rating']}, Votes: {book['ratings_count']})")
                
                if book['title'].lower().strip() not in existing_titles:
                    new_row = {col: "" for col in df.columns}
                    new_row['Author Name'] = author
                    new_row['Name of Series'] = book['title']
                    new_row['GoodReads series link'] = book['link']
                    new_row['Rating (out of 5) of Primary Book 1'] = book['rating']
                    new_row['Ratings (#) of Primary Book 1'] = book['ratings_count']
                    # Label where we got it from just like the original script
                    new_row['Website link from where this is scraped'] = "Goodreads Author Page"
                    new_rows.append(new_row)
                    existing_titles.add(book['title'].lower().strip())
                else:
                    print(f"    -> Book '{book['title']}' is already in the sheet. Skipping.")
            
            # Small delay to avoid hammering the server
            await asyncio.sleep(2)
            
        await browser.close()
        
    if new_rows:
        print(f"\nAdding {len(new_rows)} new top books to the spreadsheet...")
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        
        # Apply formatting
        os.system("python format_new_romantasy.py")
        print("Done! Formatted and saved.")
    else:
        print("\nNo new books were added (they might have all been in the sheet already).")

if __name__ == "__main__":
    asyncio.run(main())
