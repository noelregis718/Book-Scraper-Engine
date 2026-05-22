import asyncio
import os
import sys
import pandas as pd
import re
from playwright.async_api import async_playwright

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import AmazonScraper

async def verify_sequence():
    # SETTINGS FOR WEREWOLVES & SHIFTERS
    INPUT_FILE = r"E:\Internship\PocketFM\Amazon Keyword - Werewolves & Shifters.xlsx"
    SEARCH_URL = "https://www.amazon.com/s?k=Werewolves+%26+Shifters&i=stripbooks&crid=1VFS1NEXMRVWD&sprefix=werewolves+%26+shifters%2Cstripbooks%2C432&ref=nb_sb_noss_1"
    
    # Target ASINs extracted manually from your latest books
    asin1 = "B0DGDZ7GDR" # Lift Her Up
    asin2 = "B07R9XDP7B" # Mysteries of Dragon's Island
    title1 = "Lift Her Up (Kaid Ranch Shifters Book 3)"
    title2 = "Mysteries of Dragon's Island: (A Paranormal Shifter Romance Series)"

    print(f"Target 1 (Second-to-Last): {title1} (ASIN: {asin1})")
    print(f"Target 2 (Last): {title2} (ASIN: {asin2})")
    print("-" * 50)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        amz = AmazonScraper()
        print("[System] Setting US Location (90016)...")
        await page.goto("https://www.amazon.com")
        await amz.set_amazon_location(page, "90016")
        
        found1_page = None
        found2_page = None
        
        # Starting from Page 15 as requested by the user
        for p_num in range(15, 101):
            url = f"{SEARCH_URL}&page={p_num}"
            print(f"[Page {p_num}] Scanning...")
            
            try:
                await page.goto(url, wait_until="load", timeout=60000)
                await asyncio.sleep(4)
                
                # Check for CAPTCHA
                title = await page.title()
                if "Sorry! Something went wrong" in title or "Robot Check" in title:
                    print("  [ALERT] CAPTCHA detected! Please solve it.")
                    await asyncio.sleep(20) # Wait for manual solve
                
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
                items = await page.query_selector_all('[data-asin]')
                asins_on_page = []
                for item in items:
                    a = await item.get_attribute('data-asin')
                    if a and a != 'N/A': asins_on_page.append(a)
                
                if asin1 in asins_on_page:
                    found1_page = p_num
                    print(f"  -> FOUND Target 1 on Page {p_num}")
                if asin2 in asins_on_page:
                    found2_page = p_num
                    print(f"  -> FOUND Target 2 on Page {p_num}")
                
                if found1_page and found2_page:
                    break
            except Exception as e:
                print(f"  [Error] Page {p_num}: {e}")
                continue

        print("\n" + "="*50)
        print("SEQUENCE VERIFICATION RESULTS:")
        if found1_page or found2_page:
            if found1_page: print(f"Book 1 (Second-to-last): Page {found1_page}")
            if found2_page: print(f"Book 2 (Last):           Page {found2_page}")
        else:
            print("Neither target was found in the first 100 pages.")
        print("="*50)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_sequence())
