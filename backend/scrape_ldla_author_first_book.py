import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"e:\Internship\PocketFM\LDLA_Combined.xlsx"

def clean_title_for_comparison(title):
    if not isinstance(title, str):
        return ""
    t = str(title).lower()
    t = re.sub(r'\(.*?\)', '', t)
    t = re.sub(r'\[.*?\]', '', t)
    t = re.split(r'[:\-—]', t)[0]
    t = re.sub(r'[^\w\s]', '', t)
    return t.strip()

async def process_author(author, existing_titles, scraper, context):
    print(f"\n--- Checking author: {author} ---")
    page = await context.new_page()
    try:
        books = await scraper.search_author_books_with_links(page, author, max_books=1)
        if not books:
            print(f"No books found for author {author}.")
            return None
            
        top_book = books[0]
        top_title = top_book['title']
        clean_top = clean_title_for_comparison(top_title)
        
        for existing in existing_titles:
            clean_exist = clean_title_for_comparison(existing)
            if clean_top == clean_exist or clean_top in clean_exist or clean_exist in clean_top:
                if len(clean_top) > 2 and len(clean_exist) > 2:
                    print(f"Top book '{top_title}' seems to already exist in sheet as '{existing}'. Skipping.")
                    return None
                    
        print(f"Found NEW top book '{top_title}' for {author}. Scraping details...")
        
        book_link = top_book['link']
        details = await scraper.scrape_goodreads_data(context, top_title, author, existing_url=book_link)
        
        if details:
            return {
                'Name of Series': top_title,
                'Author Name': author,
                'Publisher': '',
                'GoodReads series link': details.get("GoodReads_Series_URL") if details.get("GoodReads_Series_URL") not in ["N/A", None] else details.get("GoodReads_Book_URL", ""),
                'Number of PRIMARY books in the series': details.get("Num_Primary_Books", ""),
                'Rating (out of 5) of Primary Book 1': details.get("Book1_Rating") if details.get("Book1_Rating") not in ["N/A", None] else details.get("GoodReads_Rating", ""),
                'Ratings (#) of Primary Book 1': details.get("Book1_Num_Ratings") if details.get("Book1_Num_Ratings") not in ["N/A", None] else details.get("GoodReads_Rating_Count", ""),
                'Synopsis (if available)': details.get("Description", ""),
                'Romantasy = Yes or No?': '',
                'Romantasy Sub-Genre of series': '',
                'Name of agent in the main folder': ''
            }
        return None
    except Exception as e:
        print(f"Error processing author {author}: {e}")
        return None
    finally:
        await page.close()

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    cols_to_cast = ['GoodReads series link', 'Rating (out of 5) of Primary Book 1', 
                    'Ratings (#) of Primary Book 1', 'Number of PRIMARY books in the series', 
                    'Synopsis (if available)']
    for col in cols_to_cast:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype('object')
        
    authors = df['Author Name'].dropna().unique().tolist()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        page = await context.new_page()
        logged_in = await scraper.login_to_goodreads(page)
        if not logged_in:
            print("Login failed or timed out. Scraping might be limited or blocked.")
        await page.close()
        
        new_rows = []
        chunk_size = 5
        
        for i in range(0, len(authors), chunk_size):
            chunk = authors[i:i+chunk_size]
            
            tasks = []
            for author in chunk:
                existing_titles = df[df['Author Name'] == author]['Name of Series'].dropna().tolist()
                tasks.append(process_author(author, existing_titles, scraper, context))
                
            results = await asyncio.gather(*tasks)
            
            for res in results:
                if res:
                    new_rows.append(res)
                    print(f"Added '{res['Name of Series']}' by {res['Author Name']} to staging.")
                    
            if new_rows:
                df_new = pd.DataFrame(new_rows)
                df_new = df_new[df.columns] # Reorder to match
                df = pd.concat([df, df_new], ignore_index=True)
                df.to_excel(EXCEL_FILE, index=False)
                new_rows = []
            
        await browser.close()
        
    print(f"\nExpansion Complete! Final data saved to {EXCEL_FILE}.")
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("Final styling applied.")
    except:
        pass

if __name__ == '__main__':
    asyncio.run(main())
