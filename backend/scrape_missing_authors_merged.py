import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from classify_perez import classify_subgenre

EXCEL_FILE = r"E:\Internship\PocketFM\Bradford_Solstice_Merged_Formatted.xlsx"
MAX_CONCURRENT = 5

async def process_author(context, scraper, author, index, df, semaphore):
    async with semaphore:
        safe_author = author.encode('ascii', 'ignore').decode('ascii')
        print(f"  [Searching] Top book for {safe_author}...")
        
        try:
            # First search for the top 1 book
            page = await context.new_page()
            books = await scraper.search_author_books_with_links(page, author, max_books=1)
            await page.close()
            
            if not books:
                print(f"  [Not Found] No books found for {safe_author}")
                return
                
            top_book = books[0]
            title = top_book['title']
            safe_title = title.encode('ascii', 'ignore').decode('ascii')
            print(f"    [Found] '{safe_title}'. Scraping details...")
            
            data = await scraper.scrape_goodreads_data(context, title, author)
            if data:
                df.at[index, 'Name of Series'] = title
                
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
                
                print(f"  [Done] Finished {safe_author}'s book '{safe_title}'")
                
                # Save incrementally
                df.to_excel(EXCEL_FILE, index=False)
                try:
                    from apply_jra_style import apply_styling
                    apply_styling(EXCEL_FILE)
                except: pass
            else:
                print(f"  [Failed] Could not extract details for '{safe_title}'")
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"  [Error] {safe_author}: {err_msg}")

async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return
        
    df = pd.read_excel(EXCEL_FILE)
    
    # 1. Clean up duplicate empty rows if a populated row already exists for the author
    populated_authors = set(df[df['Name of Series'].notna() & (df['Name of Series'].str.strip() != '')]['Author Name'].dropna().tolist())
    
    empty_mask = (df['Name of Series'].isna() | (df['Name of Series'].astype(str).str.strip() == '')) & df['Author Name'].notna()
    empty_indices = df[empty_mask].index.tolist()
    
    indices_to_drop = []
    indices_to_scrape = []
    
    for idx in empty_indices:
        author = df.at[idx, 'Author Name']
        if author in populated_authors:
            indices_to_drop.append(idx)
        else:
            indices_to_scrape.append(idx)
            
    if indices_to_drop:
        print(f"Cleaning up {len(indices_to_drop)} empty rows for authors that already have books scraped.")
        df = df.drop(indices_to_drop)
        df.reset_index(drop=True, inplace=True)
        # Recalculate indices_to_scrape because index changed
        empty_mask = (df['Name of Series'].isna() | (df['Name of Series'].astype(str).str.strip() == '')) & df['Author Name'].notna()
        indices_to_scrape = df[empty_mask].index.tolist()
    
    # Also ignore non-author rows like privacy policy
    ignored_keywords = ["Cookie", "Privacy", "linktr.ee", "Children", "Laura Bradford", "Hannah Andrade", "Hillary Fazzari", "Kaitlyn Sanchez", "Rebecca Matte"]
    final_indices = []
    for idx in indices_to_scrape:
        author = str(df.at[idx, 'Author Name'])
        if not any(k.lower() in author.lower() for k in ignored_keywords):
            final_indices.append(idx)
            
    print(f"Found {len(final_indices)} authors without books that need to be scraped.")
    
    if not final_indices:
        print("Nothing to do. Saving and exiting.")
        df.to_excel(EXCEL_FILE, index=False)
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
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        tasks = []
        for idx in final_indices:
            author = df.at[idx, 'Author Name']
            tasks.append(process_author(context, scraper, author, idx, df, semaphore))
            
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
