import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os
import re
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

def simplify_title(title):
    # Remove colons and everything after
    t = title.split(':')[0]
    t = t.split('-')[0]
    # Remove parentheses
    t = re.sub(r'\(.*?\)', '', t)
    # Get just the first 4 words to make search super broad
    words = t.split()
    return " ".join(words[:4]).strip()

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format_2.xlsx')
    
    df = pd.read_excel(excel_path)
    
    # Remove junk articles that got scraped
    junk_mask = df['Name of Series'].str.contains('Bookouture signs|Subscribe to', na=False, case=False)
    if junk_mask.sum() > 0:
        print(f"Removing {junk_mask.sum()} junk rows...")
        df = df[~junk_mask].reset_index(drop=True)
        df.to_excel(excel_path, index=False)

    missing_mask = df['GoodReads series link'].isna() | (df['GoodReads series link'] == 'N/A') | (df['Synopsis (if available)'] == 'N/A')
    missing_indices = df.index[missing_mask].tolist()
    
    print(f"Found {len(missing_indices)} books missing full Goodreads data.")
    if len(missing_indices) == 0: return

    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await scraper.login_to_goodreads(page)
        await page.close()
        
        for idx in missing_indices:
            raw_title = str(df.at[idx, 'Name of Series'])
            author = str(df.at[idx, 'Author Name']) if pd.notna(df.at[idx, 'Author Name']) else ""
            
            # Clean title
            clean_title = raw_title.replace('', "'")
            short_title = simplify_title(clean_title)
            
            print(f"\n[Fallback] Original: {raw_title}")
            print(f"           Searching Goodreads for: {short_title} {author}")
            
            data = await scraper.scrape_goodreads_data(context, title=short_title, author=author)
            
            if data:
                gr_link = data.get("GoodReads_Book_URL", "N/A")
                if gr_link == "N/A": gr_link = data.get("GoodReads_Series_URL", "N/A")
                
                df.at[idx, 'GoodReads series link'] = gr_link
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get("Num_Primary_Books", "N/A")
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = data.get("Book1_Rating", "N/A")
                df.at[idx, 'Ratings (#) of Primary Book 1'] = data.get("Book1_Num_Ratings", "N/A")
                df.at[idx, 'Synopsis (if available)'] = data.get("Description", "N/A")
                print(f"      [Success] Full details extracted!")
            else:
                print(f"      [Failed] Goodreads could not find it even with short title.")
                
            df.to_excel(excel_path, index=False)
            
        print(f"\n--- Scrape Complete! Excel file updated. ---")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
