import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper
from apply_jra_style import apply_styling

try:
    from classify_perez import classify_subgenre
except ImportError:
    try:
        from classify_root_literary import classify_subgenre
    except ImportError:
        def classify_subgenre(text): return ""

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'New_Agency.xlsx')
MAX_CONCURRENT = 2 # Lowered slightly due to multiple page navigations per author

excel_lock = asyncio.Lock()

async def process_author(context, scraper, df, idx, author, semaphore):
    async with semaphore:
        safe_author = author.encode('ascii', 'ignore').decode('ascii') if author else 'Unknown'
        print(f"[{idx+2}] Processing Author: {safe_author}", flush=True)
        
        try:
            books_data = await scraper.scrape_top_books_by_author(context, author, count=2)
            if not books_data:
                print(f"[{idx+2}] No books found for {safe_author}.", flush=True)
                return
                
            print(f"[{idx+2}] Successfully extracted {len(books_data)} books for {safe_author}.", flush=True)
            
            async with excel_lock:
                # We need to reload df inside lock to ensure we don't overwrite other threads' appended rows
                current_df = pd.read_excel(EXCEL_FILE)
                for col in current_df.columns:
                    if current_df[col].dtype == 'object':
                        current_df[col] = current_df[col].fillna("").astype(str)
                
                # Find the row index of this author where Name of Series is empty
                # We use Author Name to find it
                mask = (current_df['Author Name'] == author) & \
                       ((current_df['Name of Series'] == '') | (current_df['Name of Series'].str.lower() == 'nan'))
                
                matching_indices = current_df.index[mask].tolist()
                
                if not matching_indices:
                    pass
                else:
                    target_idx = matching_indices[0]
                    
                    # Fill first book in target_idx
                    b1 = books_data[0]
                    current_df.at[target_idx, 'Name of Series'] = b1.get('Book_Title', '')
                    current_df.at[target_idx, 'GoodReads series link'] = str(b1.get('GoodReads_Series_URL') if b1.get('GoodReads_Series_URL') != 'N/A' else b1.get('GoodReads_Book_URL', ''))
                    current_df.at[target_idx, 'Number of PRIMARY books in the series'] = str(b1.get('Num_Primary_Books', '1'))
                    current_df.at[target_idx, 'Rating (out of 5) of Primary Book 1'] = str(b1.get('Book1_Rating', b1.get('GoodReads_Rating', 'N/A')))
                    current_df.at[target_idx, 'Ratings (#) of Primary Book 1'] = str(b1.get('Book1_Num_Ratings', b1.get('GoodReads_Rating_Count', 'N/A')))
                    syn1 = str(b1.get('Description', 'N/A'))
                    current_df.at[target_idx, 'Synopsis (if available)'] = syn1
                    
                    subg1 = classify_subgenre(syn1 + " " + b1.get('Book_Title', ''))
                    current_df.at[target_idx, 'Romantasy = Yes or No?'] = "Yes" if subg1 else "No"
                    current_df.at[target_idx, 'Romantasy Sub-Genre of series'] = subg1 if subg1 else ""
                    
                    # If there's a second book, we duplicate target_idx row and insert it below
                    if len(books_data) > 1:
                        b2 = books_data[1]
                        new_row = current_df.loc[target_idx].copy()
                        new_row['Name of Series'] = b2.get('Book_Title', '')
                        new_row['GoodReads series link'] = str(b2.get('GoodReads_Series_URL') if b2.get('GoodReads_Series_URL') != 'N/A' else b2.get('GoodReads_Book_URL', ''))
                        new_row['Number of PRIMARY books in the series'] = str(b2.get('Num_Primary_Books', '1'))
                        new_row['Rating (out of 5) of Primary Book 1'] = str(b2.get('Book1_Rating', b2.get('GoodReads_Rating', 'N/A')))
                        new_row['Ratings (#) of Primary Book 1'] = str(b2.get('Book1_Num_Ratings', b2.get('GoodReads_Rating_Count', 'N/A')))
                        syn2 = str(b2.get('Description', 'N/A'))
                        new_row['Synopsis (if available)'] = syn2
                        
                        subg2 = classify_subgenre(syn2 + " " + b2.get('Book_Title', ''))
                        new_row['Romantasy = Yes or No?'] = "Yes" if subg2 else "No"
                        new_row['Romantasy Sub-Genre of series'] = subg2 if subg2 else ""
                        
                        # Insert new_row right after target_idx
                        current_df = pd.concat([current_df.iloc[:target_idx+1], pd.DataFrame([new_row]), current_df.iloc[target_idx+1:]]).reset_index(drop=True)

                current_df.to_excel(EXCEL_FILE, index=False)
                try:
                    apply_styling(EXCEL_FILE)
                except:
                    pass
                print(f"  [Auto-Save] Progress saved after '{safe_author}'.", flush=True)

        except Exception as e:
            print(f"[{idx+2}] Error processing '{safe_author}': {e}", flush=True)

async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading Excel file: {EXCEL_FILE}", flush=True)
    df = pd.read_excel(EXCEL_FILE)
    
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna("").astype(str)
            
    tasks = []
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...", flush=True)
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        print("--- Queuing Jill Grinberg authors for top-2 books scraping ---", flush=True)
        # Find authors that belong to Jill Grinberg and have empty title
        for idx in range(len(df)):
            author = str(df.at[idx, 'Author Name']).strip()
            title = str(df.at[idx, 'Name of Series']).strip()
            
            if author and author.lower() != 'nan':
                if not title or title.lower() == 'nan':
                    tasks.append(process_author(context, scraper, df, idx, author, semaphore))
                
        print(f"Queued {len(tasks)} authors for processing.", flush=True)
        
        if tasks:
            await asyncio.gather(*tasks)
            
        await browser.close()
        
    print("ALL DONE!", flush=True)

if __name__ == '__main__':
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    asyncio.run(run_scrape())
