import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from classify_perez import classify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\Bradford_Solstice_Merged_Formatted.xlsx"
MAX_CONCURRENT = 5

async def process_book(context, scraper, title, author, index, df, semaphore):
    async with semaphore:
        safe_title = title.encode('ascii', 'ignore').decode('ascii')
        safe_author = author.encode('ascii', 'ignore').decode('ascii')
        print(f"  [Scraping] '{safe_title}' by {safe_author}...")
        
        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                link = data.get('GoodReads_Series_URL')
                if not link or link == 'N/A':
                    link = data.get('GoodReads_Book_URL', 'N/A')
                if link == 'N/A': link = ''
                    
                df.at[index, 'GoodReads series link'] = link if link else "N/A"
                df.at[index, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                
                rating = data.get('Book1_Rating')
                if not rating or rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                df.at[index, 'Rating (out of 5) of Primary Book 1'] = rating
                
                count = data.get('Book1_Num_Ratings')
                if not count or count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                df.at[index, 'Ratings (#) of Primary Book 1'] = count
                
                synopsis = data.get('Description', 'N/A')
                df.at[index, 'Synopsis (if available)'] = synopsis
                
                combined_text = str(synopsis) + " " + str(title)
                subgenre = classify_subgenre(combined_text)
                
                is_romantasy = data.get('Romantasy_Subgenre', 'No')
                if subgenre is not None:
                    df.at[index, 'Romantasy = Yes or No?'] = "Yes"
                    df.at[index, 'Romantasy Sub-Genre of series'] = subgenre
                elif is_romantasy == 'Yes':
                    df.at[index, 'Romantasy = Yes or No?'] = "Yes"
                    df.at[index, 'Romantasy Sub-Genre of series'] = "High Fantasy Court Adventure"
                else:
                    df.at[index, 'Romantasy = Yes or No?'] = "No"
                    df.at[index, 'Romantasy Sub-Genre of series'] = ""
                
                print(f"  [Done] Parsed details for '{safe_title}'")
                
                # Save incrementally
                df.to_excel(EXCEL_FILE, index=False)
                try:
                    from apply_jra_style import apply_styling
                    apply_styling(EXCEL_FILE)
                except: pass
            else:
                print(f"  [Not Found] Details for '{safe_title}'")
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"  [Error] '{safe_title}': {err_msg}")

async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return
        
    df = pd.read_excel(EXCEL_FILE)
    
    # Identify rows that have Name of Series, Author Name, but no Synopsis
    missing_mask = (
        (df['Name of Series'].notna()) & (df['Name of Series'].str.strip() != '') &
        (df['Author Name'].notna()) & (df['Author Name'].str.strip() != '') &
        (df['Synopsis (if available)'].isna() | (df['Synopsis (if available)'] == 'N/A') | (df['Synopsis (if available)'].astype(str).str.strip() == ''))
    )
    
    indices_to_scrape = df[missing_mask].index.tolist()
    print(f"Found {len(indices_to_scrape)} books that need details scraped.")
    
    if not indices_to_scrape:
        print("Nothing to do.")
        return
        
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        print(f"--- Scraping details for {len(indices_to_scrape)} books ---")
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        tasks = []
        for idx in indices_to_scrape:
            title = df.at[idx, 'Name of Series']
            author = df.at[idx, 'Author Name']
            tasks.append(process_book(context, scraper, title, author, idx, df, semaphore))
            
        await asyncio.gather(*tasks)
        
        # Final save
        df.to_excel(EXCEL_FILE, index=False)
        try:
            from apply_jra_style import apply_styling
            apply_styling(EXCEL_FILE)
            print("Final styling applied.")
        except: pass
        
        await login_page.close()
        await browser.close()
            
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(run_scrape())
