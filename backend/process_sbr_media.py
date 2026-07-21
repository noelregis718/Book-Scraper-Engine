import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

EXCEL_FILE = r"E:\Internship\PocketFM\SBR Media.xlsx"
MAX_CONCURRENT = 8

TARGET_COLUMNS = [
    'Name of Series',
    'Author Name',
    'Publisher',
    'GoodReads series link',
    'Number of PRIMARY books in the series',
    'Rating (out of 5) of Primary Book 1',
    'Ratings (#) of Primary Book 1',
    'No. of pages in Book 1',
    'Page Count (Sum of no. of pages in all primary books)',
    'Genre tags- Up to 7 tags',
    'Synopsis (if available)',
    'Genre',
    'Sub-Genre'
]

def map_genres(tags):
    tags = [str(t).lower() for t in tags if str(t)]
    # Basic mapping based on tags
    is_romantasy = any('romantasy' in t for t in tags)
    is_fantasy = any('fantasy' in t for t in tags)
    is_romance = any('romance' in t for t in tags)
    is_crime = any('crime' in t or 'thriller' in t or 'mystery' in t for t in tags)
    
    if is_romantasy:
        return 'Romantasy'
    elif is_crime:
        return 'Crime Thriller'
    elif is_romance and is_fantasy:
        return 'Romantasy'
    elif is_romance:
        return 'Romance Drama'
    elif is_fantasy:
        return 'Fantasy'
    
    return 'Unknown'

async def process_row(context, scraper, idx, row, df, semaphore):
    async with semaphore:
        title = str(row.get('Name of Series', '')).strip()
        author = str(row.get('Author Name', '')).strip()
        link = str(row.get('GoodReads series link', '')).strip()
        
        print(f"[{idx}] Scraping '{title}' by {author}...")
        try:
            # Re-scrape to get new fields
            data = await scraper.scrape_goodreads_data(context, title, author, existing_url=link if link.startswith('http') else 'N/A')
            if data:
                # Update basic fields if empty
                if not str(df.at[idx, 'GoodReads series link']).startswith('http'):
                    df.at[idx, 'GoodReads series link'] = data.get('GoodReads_Series_URL') or data.get('GoodReads_Book_URL', '')
                
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = data.get('Book1_Rating', '')
                df.at[idx, 'Ratings (#) of Primary Book 1'] = data.get('Book1_Num_Ratings', '')
                df.at[idx, 'Synopsis (if available)'] = data.get('Description', '')
                
                # New fields
                df.at[idx, 'No. of pages in Book 1'] = data.get('Num_Pages', '')
                # Approximate Page Count for now
                try:
                    num_pages = int(data.get('Num_Pages', 0))
                    num_books = int(data.get('Num_Primary_Books', 1))
                    df.at[idx, 'Page Count (Sum of no. of pages in all primary books)'] = num_pages * num_books if num_pages else ''
                except:
                    df.at[idx, 'Page Count (Sum of no. of pages in all primary books)'] = ''
                
                all_genres = data.get('All_Genres', [])
                df.at[idx, 'Genre tags- Up to 7 tags'] = ", ".join(all_genres)
                
                genre = map_genres(all_genres)
                df.at[idx, 'Genre'] = genre
                # Sub-genre can be mapped later with LLM or strict keywords
                df.at[idx, 'Sub-Genre'] = 'Needs Mapping'
                
                print(f"[{idx}] Successfully updated '{title}'!")
            else:
                print(f"[{idx}] Details not found for '{title}'.")
        except Exception as e:
            print(f"[{idx}] Error scraping '{title}': {e}")
            traceback.print_exc()

async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
    
    # 1. Modify columns
    cols_to_drop = ['Romantasy = Yes or No?', 'Romantasy Sub-Genre of series', 'Name of agent']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    # Ensure all target columns exist
    for col in TARGET_COLUMNS:
        if col not in df.columns:
            df[col] = ''
            
    # Reorder columns to match target precisely
    df = df[TARGET_COLUMNS]
            
    # Convert object columns to strings
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna("").astype(str)

    scraper = GoodreadsScraper(headless=False)
    
    tasks = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        # We only do the remaining rows
        for idx, row in df.iloc[290:].iterrows():
            tasks.append(process_row(context, scraper, idx, row, df, semaphore))
            
        if tasks:
            await asyncio.gather(*tasks)
            
        await login_page.close()
        await browser.close()
        
    print("Saving Excel...")
    df.to_excel(EXCEL_FILE, index=False)
    
    # Style it using existing script if available
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
    except: pass
    
    print("Done!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
