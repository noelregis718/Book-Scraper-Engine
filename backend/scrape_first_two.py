import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"e:\Internship\PocketFM\LDLA_Combined.xlsx"

async def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Cast columns to avoid warnings
    cols_to_cast = ['GoodReads series link', 'Rating (out of 5) of Primary Book 1', 
                    'Ratings (#) of Primary Book 1', 'Number of PRIMARY books in the series', 
                    'Synopsis (if available)']
    for col in cols_to_cast:
        if col in df.columns:
            df[col] = df[col].astype('object')
            
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = GoodreadsScraper(headless=False)
        
        page = await context.new_page()
        logged_in = await scraper.login_to_goodreads(page)
        if not logged_in:
            print("Login failed or timed out. Scraping might be limited or blocked.")
        await page.close()
        
        # ONLY DO THE FIRST TWO BOOKS
        for idx in range(2):
            row = df.iloc[idx]
            title = str(row.get('Name of Series', '')).strip()
            author = str(row.get('Author Name', '')).strip()
            
            print(f"\n[Book {idx+1}] FORCED SEARCH on Goodreads for: '{title}' by {author}")
            
            # Note: We are ignoring the existing_link so it actually searches Goodreads
            details = await scraper.scrape_goodreads_data(context, title, author, existing_url=None)
            
            if details:
                if details.get("GoodReads_Series_URL", "N/A") != "N/A":
                    df.at[idx, 'GoodReads series link'] = details["GoodReads_Series_URL"]
                elif details.get("GoodReads_Book_URL", "N/A") != "N/A":
                    df.at[idx, 'GoodReads series link'] = details["GoodReads_Book_URL"]
                    
                if details.get("Book1_Rating", "N/A") != "N/A":
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details["Book1_Rating"]
                elif details.get("GoodReads_Rating", "N/A") != "N/A":
                    df.at[idx, 'Rating (out of 5) of Primary Book 1'] = details["GoodReads_Rating"]
                    
                if details.get("Book1_Num_Ratings", "N/A") != "N/A":
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = details["Book1_Num_Ratings"]
                elif details.get("GoodReads_Rating_Count", "N/A") != "N/A":
                    df.at[idx, 'Ratings (#) of Primary Book 1'] = details["GoodReads_Rating_Count"]
                    
                if details.get("Num_Primary_Books", "1") != "N/A":
                    df.at[idx, 'Number of PRIMARY books in the series'] = details["Num_Primary_Books"]
                    
                if details.get("Description", "N/A") != "N/A":
                    df.at[idx, 'Synopsis (if available)'] = details["Description"]
                            
        df.to_excel(EXCEL_FILE, index=False)
        await browser.close()
        
    print(f"\nScraping of first 2 books complete! Saved to {EXCEL_FILE}.")

if __name__ == '__main__':
    asyncio.run(main())
