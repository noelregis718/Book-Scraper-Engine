import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import urllib.parse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\extracted_book_titles_authors.xlsx"
MAX_CONCURRENT = 5

async def aggressive_search(page, title, author):
    # Try Google Search as the ultimate fallback
    query = f"{title} {author} site:goodreads.com/book/show".strip()
    encoded_query = urllib.parse.quote_plus(query)
    
    url = f"https://www.google.com/search?q={encoded_query}"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        
        # Check for Google Captcha
        if await page.query_selector('form[action*="CaptchaRedirect"]'):
            print(f"\n    [!!! ACTION REQUIRED !!!] Google CAPTCHA detected for '{title}'! Please solve it in the browser window.")
            try:
                await page.wait_for_selector('a[href*="goodreads.com/book/show/"]', timeout=300000)
            except:
                print("    [Timeout] Google CAPTCHA not solved in 5 minutes.")
                return None
                
        # Grab first goodreads link
        links = await page.query_selector_all('a[href*="goodreads.com/book/show/"]')
        for link in links:
            href = await link.evaluate("el => el.href")
            if href and "google.com" not in href:
                return href
    except Exception as e:
        print(f"    [Aggressive] Google Search error: {e}")
        
    return None

async def process_book(scraper, context, idx, title, author, df):
    print(f"  [Aggressive] Searching for '{title}'...")
    
    search_page = await context.new_page()
    found_url = await aggressive_search(search_page, title, author)
    await search_page.close()
    
    details = await scraper.scrape_goodreads_data(
        context=context,
        title=title,
        author=author,
        existing_url=found_url if found_url else "N/A"
    )
    
    if details:
        if not author and details.get('Author_Found', '') != 'Unknown':
            df.at[idx, 'Author Name'] = details.get('Author_Found')
        
        # KEY CHANGE: Fallback to the Book URL if there is no Series URL!
        series_url = details.get('GoodReads_Series_URL', '')
        if not series_url or series_url == 'N/A':
            series_url = details.get('GoodReads_Book_URL', '')
            
        df.at[idx, 'GoodReads series link'] = series_url
        df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details.get('Book1_Rating', '')
        df.at[idx, 'Ratings (#) of Primary Book 1'] = details.get('Book1_Num_Ratings', '')
        df.at[idx, 'Number of PRIMARY books in the series'] = details.get('Num_Primary_Books', '')
        
        synopsis = details.get('Description', '')
        if synopsis and synopsis != 'N/A':
            df.at[idx, 'Synopsis (if available)'] = synopsis
        
        genres = [g for g in [details.get('Genre', ''), details.get('Sub_Genre', '')] if g and g != 'N/A']
        df.at[idx, 'Romantasy Sub-Genre of series'] = ", ".join(genres)
        df.at[idx, 'Romantasy = Yes or No?'] = "No" 
        
        print(f"  [Success] Scraped missing links/ratings for '{title}'")
    else:
        print(f"  [Failed] Could not scrape missing details for '{title}'")

async def main():
    df = pd.read_excel(EXCEL_FILE)
    scraper = GoodreadsScraper()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        tasks_to_process = []
        for idx, row in df.iterrows():
            title = str(row.get('Name of Series', '')).strip()
            author = str(row.get('Author Name', '')).strip()
            link = str(row.get('GoodReads series link', '')).strip()
            rating = str(row.get('Rating (out of 5) of Primary Book 1', '')).strip()
            
            if title.lower() == 'nan' or not title:
                continue
                
            # If link is completely missing or rating is missing, we need to process it!
            needs_scraping = False
            if link.lower() == 'nan' or link == '' or link == 'N/A':
                needs_scraping = True
            if rating.lower() == 'nan' or rating == '' or rating == 'N/A':
                needs_scraping = True
                
            if not needs_scraping:
                continue
                
            if author.lower() == 'nan':
                author = ""
                
            tasks_to_process.append((idx, title, author))
            
        print(f"\nFound {len(tasks_to_process)} books missing URLs or Ratings.")
        
        if len(tasks_to_process) == 0:
            print("No missing links found!")
            await browser.close()
            return
            
        for i in range(0, len(tasks_to_process), MAX_CONCURRENT):
            chunk = tasks_to_process[i:i + MAX_CONCURRENT]
            print(f"\n==========================================")
            print(f"Processing chunk {i//MAX_CONCURRENT + 1} ({len(chunk)} books) aggressively...")
            print(f"==========================================")
            
            coroutines = []
            for idx, title, author in chunk:
                coroutines.append(process_book(scraper, context, idx, title, author, df))
                
            await asyncio.gather(*coroutines)
            
            print(f"  [Saved] Saving progress to Excel...")
            df.to_excel(EXCEL_FILE, index=False)
            
        print("\nALL MISSING LINKS/RATINGS PROCESSED!")
        df.to_excel(EXCEL_FILE, index=False)
        
        try:
            from apply_jra_style import apply_styling
            apply_styling(EXCEL_FILE)
            print("--- Applied final styling ---")
        except Exception as e:
            print(f"Could not apply final styling: {e}")
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
