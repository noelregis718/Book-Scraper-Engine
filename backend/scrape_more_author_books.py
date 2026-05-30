import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper, normalize_title_for_search

async def main(excel_path):
    print(f"Loading Excel file: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found: {excel_path}")
        return

    # Backup original file just in case
    backup_path = excel_path.replace(".xlsx", "_backup.xlsx")
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(excel_path, backup_path)
        print(f"Created backup at {backup_path}")

    df = pd.read_excel(excel_path)
    
    # Try to find author and title columns
    author_col = next((col for col in df.columns if 'author' in str(col).lower() or ('name' in str(col).lower() and 'author' in str(col).lower())), None)
    title_col = next((col for col in df.columns if 'title' in str(col).lower() or 'series' in str(col).lower() or 'book' in str(col).lower()), None)
    
    if not author_col or not title_col:
        print("Error: Could not find author or title columns.")
        return
        
    print(f"Using '{author_col}' for authors and '{title_col}' for existing titles.")
    
    # Remove the columns we mistakenly added in the previous run if they exist
    if "First Option Title" in df.columns:
        df = df.drop(columns=["First Option Title"])
    if "First Option Link" in df.columns:
        df = df.drop(columns=["First Option Link"])

    scraper = GoodreadsScraper(headless=False)
    
    new_rows = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(page)
        print("Login complete. Starting to scrape additional books...")
        
        # We only want to process the original 124 rows, not newly appended ones.
        # But if the script restarts, we don't want to duplicate. We will track what we've already added.
        existing_combinations = set()
        for _, row in df.iterrows():
            a = str(row[author_col]).strip().lower()
            t = normalize_title_for_search(str(row[title_col]).strip())
            existing_combinations.add((a, t))

        # We'll just iterate over the authors we have
        # To avoid duplicating authors, let's get unique authors from the original set
        unique_authors = df[author_col].dropna().unique()
        
        for idx, author_name in enumerate(unique_authors):
            author_name = str(author_name).strip()
            if not author_name or author_name.lower() in ['nan', 'none', '']:
                continue
                
            print(f"[{idx+1}/{len(unique_authors)}] Searching for author: {author_name}")
            
            # Fetch up to 5 books by this author
            results = await scraper.search_author_books_with_links(page, author_name, max_books=5)
            
            added_count = 0
            if results:
                for res in results:
                    title = res.get('title', '')
                    link = res.get('link', '')
                    
                    if not title:
                        continue
                        
                    norm_found = normalize_title_for_search(title)
                    author_lower = author_name.lower()
                    
                    # If we don't already have this book for this author
                    if (author_lower, norm_found) not in existing_combinations:
                        print(f"  -> Found NEW book: {title} ({link})")
                        
                        # Find the first row in original df for this author to copy static data (like Publisher, Agent)
                        original_row = df[df[author_col] == author_name].iloc[0].copy()
                        
                        # Clear specific book data and set new title
                        # Assuming title_col is the one we want to put the new title in
                        original_row[title_col] = title
                        
                        # If there is a link column, set it
                        link_col = next((c for c in df.columns if 'link' in str(c).lower() and 'goodreads' in str(c).lower()), None)
                        if link_col:
                            original_row[link_col] = link
                            
                        # Clear ratings, synopsis etc since this is a new book
                        for col in df.columns:
                            if any(x in str(col).lower() for x in ['rating', 'synopsis', 'primary books']):
                                original_row[col] = "N/A"
                                
                        new_rows.append(original_row)
                        existing_combinations.add((author_lower, norm_found))
                        added_count += 1
                        
                        # Let's add up to 2 new books per author to not explode the list size
                        if added_count >= 2:
                            break
                            
            if added_count == 0:
                print(f"  -> No new books found for {author_name}")
                
            # Periodically save
            if (idx + 1) % 10 == 0 and new_rows:
                temp_df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                try:
                    temp_df.to_excel(excel_path, index=False)
                    print("  [Auto-saved progress]")
                except Exception as e:
                    print(f"  [Save Error] {e}")

        await browser.close()
        
    if new_rows:
        final_df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        final_df.to_excel(excel_path, index=False)
        print(f"\nFinished! Added {len(new_rows)} new books as new rows to {excel_path}")
    else:
        print("\nFinished! No new books were found to add.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_excel = sys.argv[1]
    else:
        target_excel = input("Please enter the path to the Excel file: ").strip()
    asyncio.run(main(target_excel))
