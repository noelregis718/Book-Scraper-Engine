import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

async def main(excel_path):
    print(f"Loading Excel file: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found: {excel_path}")
        return

    df = pd.read_excel(excel_path)
    
    # Try to find author column
    author_col = None
    for col in df.columns:
        if 'author' in str(col).lower() or 'name' in str(col).lower() and 'author' in str(col).lower():
            author_col = col
            break
            
    # Fallback to checking any column with 'author'
    if not author_col:
        for col in df.columns:
            if 'author' in str(col).lower():
                author_col = col
                break

    if not author_col:
        print("Error: Could not find an author column in the Excel sheet.")
        print(f"Available columns: {list(df.columns)}")
        author_col = input("Please type the name of the column containing author names: ").strip()
        if author_col not in df.columns:
            print("Invalid column name. Exiting.")
            return
        
    print(f"Using column '{author_col}' for author names.")
    
    if "First Option Title" not in df.columns:
        df["First Option Title"] = ""
    if "First Option Link" not in df.columns:
        df["First Option Link"] = ""
        
    # Cast target columns to object to avoid FutureWarning
    df["First Option Title"] = df["First Option Title"].astype(object)
    df["First Option Link"] = df["First Option Link"].astype(object)
        
    scraper = GoodreadsScraper(headless=False)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(page)
        print("Login complete. Starting to scrape...")
        
        for index, row in df.iterrows():
            author_name = str(row[author_col]).strip()
            
            if not author_name or author_name.lower() in ['nan', 'none', '']:
                continue
                
            # Skip if already scraped
            current_link = str(row.get("First Option Link", ""))
            if current_link and current_link.lower() not in ['nan', '', 'not found']:
                continue
                
            print(f"[{index+1}/{len(df)}] Searching for author: {author_name}")
            
            # Using existing method that searches author and gets first book option
            results = await scraper.search_author_books_with_links(page, author_name, max_books=1)
            
            if results and len(results) > 0:
                first_option = results[0]
                title = first_option.get('title', '')
                link = first_option.get('link', '')
                print(f"  -> Found: {title} ({link})")
                
                df.at[index, "First Option Title"] = title
                df.at[index, "First Option Link"] = link
            else:
                print(f"  -> No results found for {author_name}")
                df.at[index, "First Option Title"] = "Not Found"
                df.at[index, "First Option Link"] = "Not Found"
                
            # Save incrementally
            try:
                df.to_excel(excel_path, index=False)
            except Exception as e:
                print(f"  [Error] Failed to save Excel file: {e}")
            
        await browser.close()
        
    print(f"\nFinished scraping. Results saved to {excel_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_excel = sys.argv[1]
    else:
        # Fallback to a prompt if no arguments are provided
        target_excel = input("Please enter the full path to the Excel file: ").strip()
        
    asyncio.run(main(target_excel))
