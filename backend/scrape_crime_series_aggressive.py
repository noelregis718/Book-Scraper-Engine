import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def run_scraper():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(workspace_dir, "Small_Mid_Sized_Publishers_Crime_Series_Reverified.xlsx")
    output_path = os.path.join(workspace_dir, "Small_Publishers_Crime_Scraped.xlsx")

    print(f"Loading input file: {input_path}")
    if not os.path.exists(input_path):
        print("Input file not found.")
        return

    # Load dataframe
    df = pd.read_excel(input_path)
    
    # Add new columns if they don't exist
    for col in ["Synopsis (if available)", "Number of PRIMARY books in the series", "Book 1 Goodreads Rating", "Number of Book 1 Ratings", "Goodreads Series URL"]:
        if col not in df.columns:
            df[col] = ""
            
    # Convert dataframe to a format we can edit easily
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        await scraper.login_to_goodreads(page)
        
        for index, row in df.iterrows():
            title = str(row.get("Book 1 Title", "")).strip()
            author = str(row.get("Author Name", "")).strip()
            
            if not title or title.lower() == 'nan':
                continue
                
            print(f"\n[{index + 1}/{len(df)}] Scraping Goodreads data for: '{title}' by '{author}'", flush=True)
            
            try:
                # Scrape aggressive with both title and author
                data = await scraper.scrape_goodreads_data(context, title=title, author=author)
                
                if data:
                    url_to_save = data.get("GoodReads_Series_URL", "N/A")
                    if url_to_save == "N/A" or not url_to_save:
                        url_to_save = data.get("GoodReads_Book_URL", "")
                        
                    df.at[index, "Goodreads Series URL"] = url_to_save
                    df.at[index, "Number of Primary Books"] = data.get("Num_Primary_Books", "")
                    df.at[index, "Book 1 Goodreads Rating"] = data.get("Book1_Rating", "")
                    df.at[index, "Number of Book 1 Ratings"] = data.get("Book1_Num_Ratings", "")
                    df.at[index, "Synopsis (if available)"] = data.get("Description", "")
                    
                    print(f"  [Success] Captured details for '{title}'.")
                else:
                    print(f"  [Failed] Could not capture details for '{title}'.")
            except Exception as e:
                print(f"  [Error] Failed to process '{title}': {e}")
                
            # Auto-save after each book
            df.to_excel(output_path, index=False)
            print(f"  [Auto-Save] Progress saved.")
            
        await browser.close()
        
    print(f"\nScraping complete. Final dataset saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(run_scraper())
