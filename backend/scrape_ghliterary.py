import asyncio
import os
import sys
import pandas as pd
import re
import json
import urllib.parse
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import clean_text

EXCEL_FILE = r"E:\Internship\PocketFM\books_authors_corrected.xlsx"
MAX_CONCURRENT_AUTHORS = 2

AUTHORS_TO_SCRAPE = ['Lucas Astor', 'Andrew Bequette', 'Claude Bouchard', 'Dr. Fayr Barkley', 'Christopher Brooks', 'Kristie Cook', 'Dorothy Dreyer', 'Leah Elson', 'Anna Elias', 'Jonathan Fredrick', 'Rebecca Fox Starr', 'Ritchie Farrell', 'Dan Franklin', 'Liana Gardner', 'Cindy Gelber', 'Anna Gomez/Christine Brae', 'Annalisa Grant', 'Randa Handler', 'Elizabeth Heaney', 'Chuck Hustmyre', 'Elizabeth Isaacs', 'Jennifer Jaynes', 'Stu Jones', 'Kenneth Johnson', 'Simon Jackson', 'Michael Logan', 'Julieanne Lynch', 'Eugene T. Lee, esq.', 'Michele G. Miller', 'John D. Mimms', 'Peter C. Newman', 'Eva Pohler', 'Jim Potts', 'Christine Peters', 'Luke Romyn', 'Lindy Ryan', 'Jen Ruiz', 'Scott Roberts', 'Harper Sutton', 'Monique Snyman', 'Jonas Saul', 'Serita Stevens', 'Sam Shearon', 'Trixie Silvertale', 'Gareth Worthington', 'Sharrie Williams', 'Alexandrea Weis', 'Laura Gia West', 'Michael David Ward']

async def scrape_book(url, context):
    page = await context.new_page()
    await page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    data = {
        "Name of Series": "N/A",
        "GoodReads series link": url,
        "Number of PRIMARY books in the series": "1",
        "Rating (out of 5) of Primary Book 1": "N/A",
        "Ratings (#) of Primary Book 1": "N/A",
        "Synopsis (if available)": "N/A"
    }
    
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(1.5)
        
        # Title
        title_el = await page.query_selector('h1[data-testid="bookTitle"]')
        if title_el:
            data["Name of Series"] = clean_text(await title_el.inner_text())
            
        # Rating & Counts
        try:
            ld_el = await page.query_selector('script[type="application/ld+json"]')
            if ld_el:
                ld_data = json.loads(await ld_el.inner_text())
                if isinstance(ld_data, list): ld_data = ld_data[0]
                data["Rating (out of 5) of Primary Book 1"] = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                data["Ratings (#) of Primary Book 1"] = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
        except: pass

        # Synopsis
        desc_el = await page.query_selector('[data-testid="description"] .Formatted, .readable')
        if desc_el:
            data["Synopsis (if available)"] = clean_text(await desc_el.inner_text())

        # Series info
        series_link_el = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
        if series_link_el:
            series_url = await series_link_el.evaluate("el => el.href")
            data["GoodReads series link"] = series_url
            
            try:
                await page.goto(series_url, wait_until="domcontentloaded", timeout=45000)
                content = await page.content()
                m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
                if m: data["Number of PRIMARY books in the series"] = m.group(1)
                
                row1 = await page.query_selector('.listWithDividers__item, .seriesWork')
                if row1:
                    rtxt = (await row1.inner_text()).lower()
                    r_match = re.search(r'([\d.]+)\s+avg\s+rating\s+[—\-]\s+([\d,]+)\s+ratings', rtxt)
                    if r_match:
                        data["Rating (out of 5) of Primary Book 1"] = r_match.group(1)
                        data["Ratings (#) of Primary Book 1"] = r_match.group(2).replace(',', '')
            except: pass

    except Exception as e:
        print(f"Error scraping book {url}: {e}")
    finally:
        await page.close()
        
    return data

async def process_author(author, context, semaphore, existing_authors):
    if author in existing_authors:
        print(f"Skipping '{author}' - already fully scraped.")
        return []

    async with semaphore:
        if not author:
            return []
            
        search_page = await context.new_page()
        await search_page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        books = []
        try:
            print(f"Searching for author: '{author}'")
            query = author.strip()
            search_url = f"https://www.goodreads.com/search?q={urllib.parse.quote_plus(query)}"
            
            await search_page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)
            
            links = []
            current_url = search_page.url
            if "/book/show/" in current_url:
                links.append(current_url)
            else:
                elements = await search_page.query_selector_all('a.bookTitle, [data-testid="bookTitle"] a, h3 a[href*="/book/show/"]')
                for el in elements:
                    href = await el.evaluate("el => el.href")
                    if href and href not in links:
                        links.append(href)
                    if len(links) >= 3:
                        break
            
            print(f"[{author}] Found {len(links)} books. Opening {len(links)} tabs...")
            
            # Open the books concurrently
            book_tasks = [scrape_book(url, context) for url in links]
            results = await asyncio.gather(*book_tasks)
            
            for res in results:
                res["Author Name"] = author
                res["Publisher"] = "Gandolfo Helin & Fountain Literary Management"
                res["Romantasy = Yes or No?"] = ""
                res["Romantasy Sub-Genre of series"] = ""
                res["Name of agent"] = ""
                books.append(res)
                
        except Exception as e:
            print(f"Error searching author {author}: {e}")
        finally:
            await search_page.close()
            
        return books

async def run_scrape():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: Could not find {EXCEL_FILE}")
        df = pd.DataFrame()
    else:
        print(f"Loading {EXCEL_FILE}...")
        df = pd.read_excel(EXCEL_FILE)
    
    # Check existing to avoid duplicates
    existing_authors = []
    if not df.empty and "Author Name" in df.columns:
        # A simple check: if the author is already in the sheet multiple times, skip.
        # But we actually want to skip if they have ANY rows, to be safe.
        existing_authors = df["Author Name"].dropna().unique().tolist()
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_AUTHORS)
        
        tasks = [process_author(author, context, semaphore, existing_authors) for author in AUTHORS_TO_SCRAPE]
        all_results = await asyncio.gather(*tasks)
        
        await browser.close()
        
    flat_results = [book for sublist in all_results for book in sublist]
    
    if not flat_results:
        print("No new books scraped.")
        return
        
    new_df = pd.DataFrame(flat_results)
    
    desired_columns = [
        "Name of Series",
        "Author Name",
        "Publisher",
        "GoodReads series link",
        "Number of PRIMARY books in the series",
        "Rating (out of 5) of Primary Book 1",
        "Ratings (#) of Primary Book 1",
        "Synopsis (if available)",
        "Romantasy = Yes or No?",
        "Romantasy Sub-Genre of series",
        "Name of agent"
    ]
    
    for col in desired_columns:
        if col not in new_df.columns:
            new_df[col] = ""
            
    new_df = new_df[desired_columns]
    
    if not df.empty:
        final_df = pd.concat([df, new_df], ignore_index=True)
    else:
        final_df = new_df
        
    print(f"Appending {len(new_df)} new rows. Total is now {len(final_df)}.")
    final_df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
    except: pass
    
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("All done!")

if __name__ == "__main__":
    asyncio.run(run_scrape())
