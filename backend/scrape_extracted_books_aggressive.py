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
            if href and "google.com" not in href: # ensure it's not a google redirect if we can help it
                return href
    except Exception as e:
        print(f"    [Aggressive] Google Search error: {e}")
        
    return None

async def process_book(scraper, context, idx, title, author, df):
    print(f"  [Aggressive] Searching for '{title}'...")
    
    # We create a temporary page just for the aggressive search
    search_page = await context.new_page()
    found_url = await aggressive_search(search_page, title, author)
    await search_page.close()
    
    if not found_url:
        print(f"  [Failed] Aggressive search found no link for '{title}'")
        return
        
    print(f"  [Aggressive] Found URL: {found_url}")
    
    # Now use the standard scraper WITH the existing_url
    details = await scraper.scrape_goodreads_data(
        context=context,
        title=title,
        author=author,
        existing_url=found_url
    )
    
    if details:
        if not author and details.get('Author_Found', '') != 'Unknown':
            df.at[idx, 'Author Name'] = details.get('Author_Found')
        
        df.at[idx, 'GoodReads series link'] = details.get('GoodReads_Series_URL', '')
        df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details.get('Book1_Rating', '')
        df.at[idx, 'Ratings (#) of Primary Book 1'] = details.get('Book1_Num_Ratings', '')
        df.at[idx, 'Number of PRIMARY books in the series'] = details.get('Num_Primary_Books', '')
        df.at[idx, 'Synopsis (if available)'] = details.get('Description', '')
        
        genres = [g for g in [details.get('Genre', ''), details.get('Sub_Genre', '')] if g and g != 'N/A']
        df.at[idx, 'Romantasy Sub-Genre of series'] = ", ".join(genres)
        df.at[idx, 'Romantasy = Yes or No?'] = "No" 
        
        print(f"  [Success] Scraped details for '{title}'")
    else:
        print(f"  [Failed] Could not scrape details for '{title}' even with URL")

async def main():
    df = pd.read_excel(EXCEL_FILE)
    scraper = GoodreadsScraper()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Determine rows missing synopsis or link
        tasks_to_process = []
        for idx, row in df.iterrows():
            title = str(row.get('Name of Series', '')).strip()
            author = str(row.get('Author Name', '')).strip()
            synopsis = str(row.get('Synopsis (if available)', '')).strip()
            link = str(row.get('GoodReads series link', '')).strip()
            
            if title.lower() == 'nan' or not title:
                continue
                
            # If both synopsis and link are present, skip
            if synopsis.lower() != 'nan' and synopsis != '' and link.lower() != 'nan' and link != '':
                continue
                
            if author.lower() == 'nan':
                author = ""
                
            tasks_to_process.append((idx, title, author))
            
        print(f"\nFound {len(tasks_to_process)} books missing details/URL for aggressive scraping.")
        
        if len(tasks_to_process) == 0:
            print("Nothing to do!")
            await browser.close()
            return
            
        # Chunk the tasks into groups
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
            
        print("\nALL MISSING BOOKS PROCESSED!")
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
