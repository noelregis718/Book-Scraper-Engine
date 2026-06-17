import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format_2.xlsx')
    
    print(f"Loading Excel file: {excel_path}")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return

    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # 1. Login to Goodreads
        print("\n--- Goodreads Login Phase ---")
        logged_in = await scraper.login_to_goodreads(page)
        if not logged_in:
            print("Login failed or timed out. We will proceed, but some data might be restricted.")
            
        await page.close()
        
        # 2. Iterate through books
        total_books = len(df)
        print(f"\n--- Starting Aggressive Scrape for {total_books} books ---")
        
        for index, row in df.iterrows():
            title = str(row['Name of Series'])
            author = str(row['Author Name']) if pd.notna(row['Author Name']) else ""
            
            # Skip if we already have a synopsis and link (meaning it was already scraped)
            if pd.notna(row['GoodReads series link']) and str(row['GoodReads series link']).strip() not in ["", "N/A", "nan"]:
                if pd.notna(row['Synopsis (if available)']) and str(row['Synopsis (if available)']).strip() not in ["", "N/A", "nan"]:
                    print(f"[{index + 1}/{total_books}] Skipping '{title}' - already scraped.")
                    continue

            print(f"\n[{index + 1}/{total_books}] Processing: {title} by {author}")
            
            data = await scraper.scrape_goodreads_data(context, title=title, author=author)
            
            if data:
                # Prioritize Book URL if Series URL is missing or N/A
                gr_link = data.get("GoodReads_Series_URL", "N/A")
                if gr_link == "N/A" and data.get("GoodReads_Book_URL"):
                    gr_link = data.get("GoodReads_Book_URL")
                    
                df.at[index, 'GoodReads series link'] = gr_link
                df.at[index, 'Number of PRIMARY books in the series'] = data.get("Num_Primary_Books", "N/A")
                df.at[index, 'Rating (out of 5) of Primary Book 1'] = data.get("Book1_Rating", "N/A")
                df.at[index, 'Ratings (#) of Primary Book 1'] = data.get("Book1_Num_Ratings", "N/A")
                df.at[index, 'Synopsis (if available)'] = data.get("Description", "N/A")
                
                print(f"  -> Extracted details successfully.")
            else:
                print(f"  -> Failed to extract data for: {title}")
                
            # Save progress every 5 books
            if (index + 1) % 5 == 0:
                df.to_excel(excel_path, index=False)
                print(f"  [Auto-Save] Progress saved at book {index + 1}.")
                
        # Final save
        df.to_excel(excel_path, index=False)
        print(f"\n--- Scrape Complete! Data saved to {excel_path} ---")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
