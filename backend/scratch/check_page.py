import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import AmazonScraper
from playwright.async_api import async_playwright

async def check():
    amz = AmazonScraper(headless=False)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.amazon.com")
        await amz.set_amazon_location(page, "90016")
        
        base_url = "https://www.amazon.com/s?k=Paranormal+Romance&i=stripbooks&crid=2MOWCGE10UUZ2&sprefix=paranormal+romance%2Cstripbooks%2C349&ref=nb_sb_noss_1"
        
        for p_num in range(1, 401):
            target_url = base_url + f"&page={p_num}"
            print(f"Navigating to {target_url}...")
            await page.goto(target_url)
            await asyncio.sleep(5)
            
            items = await page.query_selector_all('[data-asin]')
            print(f"Page {p_num}: {len(items)} books found with ASINs")
            
            content = await page.content()
            if "A Heart for the Taking" in content:
                print(f"FOUND on Page {p_num}")
                break
            if len(items) == 0:
                print(f"Reached end of results at Page {p_num}")
                break
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())
