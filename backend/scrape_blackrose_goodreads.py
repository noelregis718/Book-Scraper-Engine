import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import sys
import os

# Ensure the backend directory is in the path so we can import goodreads_scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format.xlsx')
    
    print(f"Loading Excel file: {excel_path}")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return

    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        # Launch non-headless so you can solve CAPTCHAs if needed
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
        
        # We can close the initial login page to free up resources
        await page.close()
        
        # 2. Iterate through books
        total_books = len(df)
        print(f"\n--- Starting Aggressive Scrape for {total_books} books ---")
        
        for index, row in df.iterrows():
            title = str(row['Name of Series'])
            if pd.isna(row['Name of Series']) or str(row['Name of Series']).strip() == "":
                continue
                
            # Skip if we already have an author
            if pd.notna(row['Author Name']) and str(row['Author Name']).strip() != "":
                print(f"[{index + 1}/{total_books}] Skipping '{title}' - already has author.")
                continue

            print(f"\n[{index + 1}/{total_books}] Processing: {title}")
            
            # Use the scraper function. Author is passed as empty string so it relies only on title.
            data = await scraper.scrape_goodreads_data(context, title=title, author="")
            
            if data:
                # Update DataFrame with the mappings
                if data.get("Author_Found") and data["Author_Found"] != "N/A":
                    df.at[index, 'Author Name'] = data["Author_Found"]
                
                df.at[index, 'GoodReads series link'] = data.get("GoodReads_Series_URL", "N/A")
                df.at[index, 'Number of PRIMARY books in the series'] = data.get("Num_Primary_Books", "N/A")
                df.at[index, 'Rating (out of 5) of Primary Book 1'] = data.get("Book1_Rating", "N/A")
                df.at[index, 'Ratings (#) of Primary Book 1'] = data.get("Book1_Num_Ratings", "N/A")
                df.at[index, 'Synopsis (if available)'] = data.get("Description", "N/A")
                df.at[index, 'Romantasy Sub-Genre of series'] = data.get("Romantasy_Subgenre", "N/A")
                
                print(f"  -> Extracted Author: {data.get('Author_Found', 'N/A')}")
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
