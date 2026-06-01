import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper, clean_text, normalize_title_for_search

try:
    from apply_jra_style import apply_styling
except ImportError:
    def apply_styling(path): pass

file_lock = asyncio.Lock()

async def safe_save(df, excel_path):
    async with file_lock:
        try:
            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"  [Save Error] {e}")

async def scrape_one_book(index, title, author_for_search, df, excel_path, context, semaphore):
    async with semaphore:
        page = await context.new_page()
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        try:
            query = f"{normalize_title_for_search(title)} {author_for_search}".strip()
            search_url = f"https://www.goodreads.com/search?q={query.replace(' ', '+')}"
            print(f"[{index+1}] Searching: '{query}'")

            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2.5)

            current_url = page.url
            if "/book/show/" in current_url:
                book_url = current_url
            else:
                try:
                    first_link = await page.wait_for_selector(
                        'a.bookTitle, [data-testid="bookTitle"] a, h3 a[href*="/book/show/"]',
                        timeout=5000
                    )
                    book_url = await first_link.evaluate("el => el.href")
                except Exception:
                    print(f"[{index+1}] No result for '{title}'")
                    df.at[index, "GoodReads series link"] = "N/A"
                    await safe_save(df, excel_path)
                    return

            await page.goto(book_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(1.5)

            import json, re

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

            df.at[index, "GoodReads series link"] = series_url
            df.at[index, "Number of PRIMARY books in the series"] = num_primary
            df.at[index, "Rating (out of 5) of Primary Book 1"] = book1_rating
            df.at[index, "Ratings (#) of Primary Book 1"] = book1_ratings
            df.at[index, "Synopsis (if available)"] = description

            print(f"[{index+1}] Done: '{title}'")
            await safe_save(df, excel_path)

        except Exception as e:
            print(f"[{index+1}] Error on '{title}': {e}")
        finally:
            try:
                await page.close()
            except: pass

def apply_11_columns(excel_path):
    df = pd.read_excel(excel_path)
    ELEVEN_COLUMN_HEADERS = [
        "Name of Series", "Author Name", "Publisher", "GoodReads series link", 
        "Number of PRIMARY books in the series", "Rating (out of 5) of Primary Book 1", 
        "Ratings (#) of Primary Book 1", "Synopsis (if available)", 
        "Romantasy = Yes or No?", "Romantasy Sub-Genre of series", "Name of agent"
    ]
    if 'Book Name' in df.columns:
        df.rename(columns={'Book Name': 'Name of Series'}, inplace=True)
    
    for c in ELEVEN_COLUMN_HEADERS:
        if c not in df.columns:
            df[c] = ""
            
    df = df[ELEVEN_COLUMN_HEADERS]
    df.to_excel(excel_path, index=False)
    print("Applied 11-column format.")

async def scrape_ffr(excel_path):
    print(f"Loading: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: File not found — {excel_path}")
        return

    apply_11_columns(excel_path)
    df = pd.read_excel(excel_path)

    for col in ["GoodReads series link", "Number of PRIMARY books in the series",
                "Rating (out of 5) of Primary Book 1", "Ratings (#) of Primary Book 1",
                "Synopsis (if available)"]:
        df[col] = df[col].astype(object)

    scraper = GoodreadsScraper(headless=False)
    semaphore = asyncio.Semaphore(10)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        login_context = await browser.new_context()
        login_page = await login_context.new_page()
        print("Logging in to Goodreads...")
        await scraper.login_to_goodreads(login_page)
        storage_state = await login_context.storage_state()
        await login_context.close()
        
        main_context = await browser.new_context(storage_state=storage_state)

        tasks = []
        for index, row in df.iterrows():
            title = str(row.get("Name of Series", "")).strip()
            author = str(row.get("Author Name", "")).strip()

            if not title or title.lower() in ["nan", ""]:
                continue

            current_link = str(row.get("GoodReads series link", ""))
            if current_link and current_link not in ["nan", "", "N/A"]:
                continue

            author_for_search = author if author.lower() not in ["nan", ""] else ""

            tasks.append(scrape_one_book(index, title, author_for_search, df, excel_path, main_context, semaphore))

        print(f"Starting to scrape {len(tasks)} books...")
        await asyncio.gather(*tasks)
        print("\nScraping complete!")
        
        try:
            await main_context.close()
            await browser.close()
        except: pass

    print("Reapplying styling...")
    try:
        apply_styling(excel_path)
    except: pass
    print("All done!")

if __name__ == "__main__":
    target = r"E:\Internship\PocketFM\first_for_romance_books.xlsx"
    asyncio.run(scrape_ffr(target))
