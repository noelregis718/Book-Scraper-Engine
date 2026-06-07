import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def scrape_first():
    file_path = r'E:\Internship\PocketFM\deborah_harris_merged.xlsx'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    print(f"Loading {file_path}...")
    df = pd.read_excel(file_path)
    
    if df.empty:
        print("Excel file is empty.")
        return
        
    idx = 0
    title = str(df.at[idx, 'Name of Series']).strip()
    author = str(df.at[idx, 'Author Name']).strip()
    
    print(f"Target: Row 0 -> '{title}' by {author}")
    
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        login_page = await context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        
        print(f"Scraping metadata for '{title}'...")
        try:
            data = await scraper.scrape_goodreads_data(context, title, author)
            
            if data:
                s_link = data.get('GoodReads_Series_URL')
                if not s_link or s_link == 'N/A':
                    s_link = data.get('GoodReads_Book_URL', 'N/A')
                if s_link == 'N/A': s_link = ''
                df.at[idx, 'GoodReads series link'] = s_link
                
                df.at[idx, 'Number of PRIMARY books in the series'] = data.get('Num_Primary_Books', 1)
                
                rating = data.get('Book1_Rating', 'N/A')
                if rating == 'N/A': rating = data.get('GoodReads_Rating', 'N/A')
                df.at[idx, 'Rating (out of 5) of Primary Book 1'] = rating
                
                count = data.get('Book1_Num_Ratings', 'N/A')
                if count == 'N/A': count = data.get('GoodReads_Rating_Count', 'N/A')
                df.at[idx, 'Ratings (#) of Primary Book 1'] = count
                
                df.at[idx, 'Synopsis (if available)'] = data.get('Description', 'N/A')
                
                print(f"Success! Data extracted for '{title}'.")
            else:
                print(f"Failed to extract details for '{title}'.")
                
        except Exception as e:
            print(f"Error scraping '{title}': {e}")
            
        await login_page.close()
        await browser.close()
        
    print("Saving Excel file...")
    df.to_excel(file_path, index=False)
    
    try:
        from style_books_authors import apply_styling
        apply_styling(file_path)
    except Exception as e:
        print(f"Could not apply styling: {e}")

if __name__ == "__main__":
    asyncio.run(scrape_first())
