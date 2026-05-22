import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper, clean_text, normalize_title_for_search
from apply_jra_style import apply_styling

file_lock = asyncio.Lock()

async def safe_save(df, excel_path):
    async with file_lock:
        try:
            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"  [Save Error] {e}")

async def find_new_books_for_author(author, existing_titles, shared_context, semaphore):
    async with semaphore:
        page = await shared_context.new_page()
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        new_books = []
        try:
            query = author.strip()
            search_url = f"https://www.goodreads.com/search?q={query.replace(' ', '+')}&search_type=books"
            print(f"[{author}] Hunting for new books...")
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)

            rows = await page.query_selector_all('tr[itemtype="http://schema.org/Book"]')
            
            for row in rows:
                if len(new_books) >= 50:
                    break
                
                title_el = await row.query_selector('a.bookTitle')
                author_el = await row.query_selector('a.authorName')
                
                if not title_el or not author_el:
                    continue
                    
                title = await title_el.inner_text()
                result_author = await author_el.inner_text()
                
                if author.lower() not in result_author.lower() and result_author.lower() not in author.lower():
                    continue
                    
                clean_t = normalize_title_for_search(title).lower().strip()
                
                is_duplicate = False
                for ex_t in existing_titles:
                    if clean_t in ex_t or ex_t in clean_t:
                        is_duplicate = True
                        break
                        
                if not is_duplicate:
                    book_url = await title_el.evaluate("el => el.href")
                    new_books.append({"title": title.strip(), "url": book_url, "author": author})
                    existing_titles.add(clean_t)
            
            print(f"[{author}] Found {len(new_books)} new books.")
        except Exception as e:
            print(f"[{author}] Error finding books: {e}")
        finally:
            await page.close()
            
        return new_books

async def scrape_book_details(index, book_info, df, excel_path, shared_context, semaphore):
    async with semaphore:
        page = await shared_context.new_page()
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        title = book_info['title']
        author = book_info['author']
        book_url = book_info['url']
        
        try:
            print(f"[{index}] Scraping details for '{title}'...")
            await page.goto(book_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(1.5)

            import json

            avg_rating, rating_count = "N/A", "N/A"
            try:
                ld_el = await page.query_selector('script[type="application/ld+json"]')
                if ld_el:
                    ld_data = json.loads(await ld_el.inner_text())
                    if isinstance(ld_data, list): ld_data = ld_data[0]
                    avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                    rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
            except: pass

            description = "N/A"
            desc_el = await page.query_selector('[data-testid="description"] .Formatted, .readable')
            if desc_el:
                description = clean_text(await desc_el.inner_text())

            series_url = book_url
            series_link_el = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
            if series_link_el:
                series_url = await series_link_el.evaluate("el => el.href")

            num_primary = "1"
            book1_rating = avg_rating
            book1_ratings = rating_count
            if "/series/" in series_url:
                try:
                    await page.goto(series_url, wait_until="domcontentloaded", timeout=45000)
                    content = await page.content()
                    m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
                    if m: num_primary = m.group(1)
                    row1 = await page.query_selector('.listWithDividers__item, .seriesWork')
                    if row1:
                        rtxt = (await row1.inner_text()).lower()
                        r_match = re.search(r'([\d.]+)\s+avg\s+rating\s+[—\-]\s+([\d,]+)\s+ratings', rtxt)
                        if r_match:
                            book1_rating = r_match.group(1)
                            book1_ratings = r_match.group(2).replace(',', '')
                except: pass

            async with file_lock:
                df.at[index, "GoodReads series link"] = series_url
                df.at[index, "Number of PRIMARY books in the series"] = num_primary
                df.at[index, "Rating (out of 5) of Primary Book 1"] = book1_rating
                df.at[index, "Ratings (#) of Primary Book 1"] = book1_ratings
                df.at[index, "Synopsis (if available)"] = description

            print(f"[{index}] Done: '{title}'")
            await safe_save(df, excel_path)

        except Exception as e:
            print(f"[{index}] Error on '{title}': {e}")
        finally:
            await page.close()


async def main(excel_path):
    print(f"Loading: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: File not found")
        return

    df = pd.read_excel(excel_path)
    
    # Cast target columns to object
    for col in ["GoodReads series link", "Number of PRIMARY books in the series",
                "Rating (out of 5) of Primary Book 1", "Ratings (#) of Primary Book 1",
                "Synopsis (if available)"]:
        if col in df.columns:
            df[col] = df[col].astype(object)

    # Build existing author -> titles map
    author_books = {}
    for _, row in df.iterrows():
        a = str(row.get("Author Name", "")).strip()
        t = str(row.get("Name of Series", "")).strip()
        if a and a != "nan" and t and t != "nan":
            if a not in author_books:
                author_books[a] = set()
            author_books[a].add(normalize_title_for_search(t).lower().strip())

    authors_to_search = list(author_books.keys())
    print(f"Found {len(authors_to_search)} unique authors to search for new books.")

    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(5)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        login_context = await browser.new_context()
        login_page = await login_context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        storage_state = await login_context.storage_state()
        await login_context.close()
        
        shared_context = await browser.new_context(storage_state=storage_state)
        
        # Step 1: Find new books
        print("\n--- PHASE 1: Finding up to 2 new books per author ---")
        find_tasks = []
        for author in authors_to_search:
            find_tasks.append(find_new_books_for_author(author, author_books[author], shared_context, semaphore))
            
        results = await asyncio.gather(*find_tasks)
        
        all_new_books = []
        for res in results:
            all_new_books.extend(res)
            
        print(f"\nTotal new books found: {len(all_new_books)}")
        
        if not all_new_books:
            print("No new books to append.")
            await shared_context.close()
            await browser.close()
            return
            
        # Append to DataFrame
        new_rows = []
        for b in all_new_books:
            new_rows.append({
                "Name of Series": b['title'],
                "Author Name": b['author'],
                "Publisher": "",
                "GoodReads series link": "N/A",
                "Number of PRIMARY books in the series": "N/A",
                "Rating (out of 5) of Primary Book 1": "N/A",
                "Ratings (#) of Primary Book 1": "N/A",
                "Synopsis (if available)": "N/A",
                "Romantasy = Yes or No?": "",
                "Romantasy Sub-Genre of series": "",
                "Name of agent": "Darley Anderson"
            })
            
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        # Re-cast columns if pd.concat removed object type
        for col in ["GoodReads series link", "Synopsis (if available)"]:
            df[col] = df[col].astype(object)
            
        await safe_save(df, excel_path)
        
        # Step 2: Scrape details for new books
        print("\n--- PHASE 2: Scraping details for new books ---")
        scrape_tasks = []
        # Get indices of newly added books
        start_idx = len(df) - len(all_new_books)
        
        for i, b in enumerate(all_new_books):
            idx = start_idx + i
            scrape_tasks.append(scrape_book_details(idx, b, df, excel_path, shared_context, semaphore))
            
        await asyncio.gather(*scrape_tasks)
        
        await shared_context.close()
        await browser.close()

    print("Reapplying styling...")
    apply_styling(excel_path)
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", excel_path], shell=True)
    print("All done!")

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(base, "Darley_Anderson_Formatted.xlsx")
    asyncio.run(main(target))
