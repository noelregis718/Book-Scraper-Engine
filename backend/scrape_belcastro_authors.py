import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright

async def get_author_name(context, url):
    page = await context.new_page()
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
                await page.close()
                return name.strip()
                
        await page.close()
        return "Unknown"
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        await page.close()
        return "Unknown"

async def process_row(idx, link, context, df, semaphore, file_lock, excel_path):
    async with semaphore:
        print(f"Fetching author for row {idx+2}: {link}")
        author_name = await get_author_name(context, link)
        print(f"  -> Found: {author_name}")
        
        if author_name and author_name != "Unknown":
            async with file_lock:
                df.at[idx, "Author Name"] = author_name
                try:
                    df.to_excel(excel_path, index=False)
                except:
                    pass

async def scrape_missing_authors():
    excel_path = r"E:\Internship\PocketFM\Belcastro_Agency_Formatted.xlsx"
    print(f"Loading {excel_path}...")
    
    df = pd.read_excel(excel_path)
    
    rows_to_update = []
    for idx, row in df.iterrows():
        author = str(row.get("Author Name", "")).strip()
        link = str(row.get("GoodReads series link", "")).strip()
        
        if link and link.startswith("http") and (author in ["Unknown", "N/A", "[Author name to be fetched]", "", "nan"]):
            rows_to_update.append((idx, link))
            
    print(f"Found {len(rows_to_update)} authors to fetch.")
    if not rows_to_update:
        return
        
    file_lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(10) # 10 tabs concurrently
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        tasks = [
            process_row(idx, link, context, df, semaphore, file_lock, excel_path)
            for idx, link in rows_to_update
        ]
        
        await asyncio.gather(*tasks)
        await browser.close()
        
    df.to_excel(excel_path, index=False)
    print("Done fetching missing authors with 10 tabs!")

if __name__ == "__main__":
    asyncio.run(scrape_missing_authors())
