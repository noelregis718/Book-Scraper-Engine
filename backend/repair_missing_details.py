import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper

file_lock = asyncio.Lock()

async def safe_save(df, excel_path):
    async with file_lock:
        try:
            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"  [Save Error] {e}")

async def repair_row(index, title, author, existing_url, df, excel_path, scraper, browser, storage_state, semaphore):
    async with semaphore:
        context = await browser.new_context(storage_state=storage_state)
        try:
            print(f"[{index+2}] Repairing: {title} by {author}")
            
            # scrape_goodreads_data does the search (if no url), navigation, and extraction
            data = await scraper.scrape_goodreads_data(
                context=context,
                title=title,
                author=author,
                existing_url=existing_url
            )
            
            if data and data.get("GoodReads_Book_URL"):
                df.at[index, "GoodReads series link"] = data.get("GoodReads_Series_URL", data.get("GoodReads_Book_URL"))
                df.at[index, "Number of PRIMARY books in the series"] = data.get("Num_Primary_Books", "1")
                df.at[index, "Rating (out of 5) of Primary Book 1"] = data.get("Book1_Rating", data.get("GoodReads_Rating", "N/A"))
                df.at[index, "Ratings (#) of Primary Book 1"] = data.get("Book1_Num_Ratings", data.get("GoodReads_Rating_Count", "N/A"))
                df.at[index, "Synopsis (if available)"] = data.get("Description", "N/A")
                
                print(f"[{index+2}] Successfully repaired: {title}")
                await safe_save(df, excel_path)
            else:
                print(f"[{index+2}] Failed to find/repair data for: {title}")
                
        except Exception as e:
            print(f"[{index+2}] Error repairing '{title}': {e}")
        finally:
            try:
                await context.close()
            except: pass

async def main(excel_path):
    print(f"Loading Excel file: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found: {excel_path}")
        return

    df = pd.read_excel(excel_path)
    
    # Target columns need to be object type
    cols_to_update = [
        "GoodReads series link", 
        "Number of PRIMARY books in the series",
        "Rating (out of 5) of Primary Book 1", 
        "Ratings (#) of Primary Book 1",
        "Synopsis (if available)"
    ]
    for col in cols_to_update:
        if col in df.columns:
            df[col] = df[col].astype(object)
        else:
            df[col] = "N/A"
            df[col] = df[col].astype(object)
            
    title_col = next((col for col in df.columns if 'title' in str(col).lower() or 'series' in str(col).lower() or 'book' in str(col).lower()), None)
    author_col = next((col for col in df.columns if 'author' in str(col).lower() or ('name' in str(col).lower() and 'author' in str(col).lower())), None)
    
    if not title_col or not author_col:
        print("Error: Could not find title or author columns.")
        return

    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(10) # 10 concurrent tabs
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        login_context = await browser.new_context()
        login_page = await login_context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        storage_state = await login_context.storage_state()
        await login_context.close()
        print("Login complete. Starting repair...\n")

        tasks = []
        for index, row in df.iterrows():
            title = str(row.get(title_col, "")).strip()
            author = str(row.get(author_col, "")).strip()
            synopsis = str(row.get("Synopsis (if available)", "")).strip()
            book_url = str(row.get("GoodReads series link", "")).strip()
            
            if not title or title.lower() in ["nan", "none"]:
                continue
                
            needs_repair = False
            # Needs repair if missing link OR missing synopsis
            if not book_url or not book_url.startswith("http") or book_url.lower() == "n/a":
                needs_repair = True
            elif not synopsis or synopsis.lower() in ["nan", "none", "", "n/a"]:
                needs_repair = True
                
            if needs_repair:
                # If the URL is bad, pass N/A so the scraper knows it has to search
                existing_url = book_url if book_url.startswith("http") else "N/A"
                
                tasks.append(repair_row(
                    index, title, author, existing_url, df, excel_path, 
                    scraper, browser, storage_state, semaphore
                ))

        print(f"Found {len(tasks)} books with missing links or details.")
        await asyncio.gather(*tasks)

        await browser.close()
        
    print(f"\nFinished repairing all missing details. Saved to {excel_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_excel = sys.argv[1]
    else:
        target_excel = input("Please enter the path to the Excel file: ").strip()
    asyncio.run(main(target_excel))
