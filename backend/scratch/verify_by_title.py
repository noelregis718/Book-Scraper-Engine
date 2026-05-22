import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import AmazonScraper, clean_text

async def verify_by_title():
    INPUT_FILE = r"E:\Internship\PocketFM\Amazon Keyword - paranormal Romance.xlsx"
    SEARCH_URL = "https://www.amazon.com/s?k=Paranormal+Romance&i=stripbooks&crid=2MOWCGE10UUZ2&sprefix=paranormal+romance%2Cstripbooks%2C349&ref=nb_sb_noss_1"
    
    print(f"Loading Excel...")
    df = pd.read_excel(INPUT_FILE)
    
    # Get last two books
    last_two = df.dropna(subset=['Book Title']).tail(2)
    book2_title = clean_text(last_two.iloc[1]['Book Title']) # Last
    book1_title = clean_text(last_two.iloc[0]['Book Title']) # Second to last

    # Simplify titles for broader matching (first 30 chars, no special chars)
    t1_short = book1_title[:30].strip()
    t2_short = book2_title[:30].strip()

    print(f"Target 1 (Second-to-Last): '{t1_short}...'")
    print(f"Target 2 (Last): '{t2_short}...'")
    print("-" * 50)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        amz = AmazonScraper()
        try:
            await page.goto("https://www.amazon.com")
            await amz.set_amazon_location(page, "90016")
        except Exception as e:
            print(f"Location sync error (ignoring): {e}")
        
        found1_page = None
        found2_page = None
        
        for p_num in range(15, 101):
            url = f"{SEARCH_URL}&page={p_num}"
            print(f"[Page {p_num}] Scanning by Title...")
            
            await page.goto(url, wait_until="load", timeout=60000)
            await asyncio.sleep(4)
            
            title = await page.title()
            if "Spend less" in title or "Smile more" in title:
                print("  [ALERT] Amazon Dog Page (Error) detected! Waiting 10s and retrying...")
                await asyncio.sleep(10)
                await page.reload()
                await asyncio.sleep(5)
            
            try:
                await page.evaluate("if(document.body) window.scrollTo(0, document.body.scrollHeight)")
            except:
                pass
            await asyncio.sleep(2)
            
            content = await page.content()
            
            if t1_short in content and not found1_page:
                found1_page = p_num
                print(f"  -> FOUND Target 1 ('{t1_short}') on Page {p_num}")
            if t2_short in content and not found2_page:
                found2_page = p_num
                print(f"  -> FOUND Target 2 ('{t2_short}') on Page {p_num}")
            
            if found1_page and found2_page:
                break

        print("\n" + "="*50)
        print("TITLE SEARCH RESULTS:")
        if found1_page and found2_page:
            print(f"Book 1 (Second-to-last): Page {found1_page}")
            print(f"Book 2 (Last):           Page {found2_page}")
            if found1_page == found2_page:
                print("CONCLUSION: Both books are on the SAME page.")
            elif found2_page == found1_page + 1:
                print("CONCLUSION: Sequential pages (Page X and Page X+1).")
            else:
                print(f"CONCLUSION: Non-sequential pages (Gap of {found2_page - found1_page} pages).")
        else:
            if not found1_page: print(f"Target 1 NOT FOUND.")
            if not found2_page: print(f"Target 2 NOT FOUND.")
        print("="*50)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_by_title())
