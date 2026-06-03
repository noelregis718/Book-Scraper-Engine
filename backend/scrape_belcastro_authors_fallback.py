import asyncio
import os
import re
import pandas as pd
from playwright.async_api import async_playwright

async def get_author_from_goodreads_book(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        selectors = [
            '[data-testid="authorName"]',
            '.ContributorLink__name',
            '.authorName',
            '.authorName__container span[itemprop="name"]',
            'span.ContributorLink__name'
        ]
        for selector in selectors:
            author_el = await page.query_selector(selector)
            if author_el:
                name = await author_el.inner_text()
                return name.strip()
        return "Unknown"
    except:
        return "Unknown"

async def fallback_search_author(context, title):
    page = await context.new_page()
    try:
        # Search Brave for the book and author
        clean_title = re.sub(r'[^\w\s]', '', title)
        query = f'"{clean_title}" book author goodreads'
        url = f"https://search.brave.com/search?q={query.replace(' ', '+')}"
        
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        
        # Try to find a goodreads /book/show/ link
        book_link_el = await page.query_selector('a[href*="goodreads.com/book/show/"]')
        if book_link_el:
            book_url = await book_link_el.evaluate("el => el.href")
            # Navigate to the book page and grab author
            author = await get_author_from_goodreads_book(page, book_url)
            await page.close()
            return author
            
        # If no goodreads link, try to parse the Brave snippet directly
        snippets = await page.query_selector_all('.snippet-description')
        for snip in snippets:
            text = await snip.inner_text()
            # Look for "by [Author]"
            match = re.search(r'\bby\s+([A-Z][a-zA-Z\.\-]+\s+[A-Z][a-zA-Z\.\-]+)', text)
            if match:
                await page.close()
                return match.group(1).strip()
                
        await page.close()
        return "Unknown"
    except Exception as e:
        print(f"Error on fallback for {title}: {e}")
        await page.close()
        return "Unknown"

async def process_row(idx, title, context, df, semaphore, file_lock, excel_path):
    async with semaphore:
        print(f"Fallback searching for row {idx+2}: {title}")
        author_name = await fallback_search_author(context, title)
        print(f"  -> Found: {author_name}")
        
        if author_name and author_name != "Unknown":
            async with file_lock:
                df.at[idx, "Author Name"] = author_name
                try:
                    df.to_excel(excel_path, index=False)
                except:
                    pass

async def main():
    excel_path = r"E:\Internship\PocketFM\Belcastro_Agency_Formatted.xlsx"
    print(f"Loading {excel_path}...")
    df = pd.read_excel(excel_path)
    
    rows_to_update = []
    for idx, row in df.iterrows():
        author = str(row.get("Author Name", "")).strip()
        title = str(row.get("Name of Series", "")).strip()
        
        if title and author in ["Unknown", "N/A", "[Author name to be fetched]", "", "nan"]:
            rows_to_update.append((idx, title))
            
    print(f"Found {len(rows_to_update)} 'Unknown' authors remaining.")
    if not rows_to_update:
        return
        
    file_lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(10) # 10 tabs concurrently
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Set realistic user agent for brave search
        await context.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        tasks = [
            process_row(idx, title, context, df, semaphore, file_lock, excel_path)
            for idx, title in rows_to_update
        ]
        
        await asyncio.gather(*tasks)
        await browser.close()
        
    df.to_excel(excel_path, index=False)
    print("Done fetching fallback authors!")

if __name__ == "__main__":
    asyncio.run(main())
