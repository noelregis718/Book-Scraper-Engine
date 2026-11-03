import asyncio
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from goodreads_scraper import GoodreadsScraper
from romantasy_analyzer import identify_romantasy_subgenre
from playwright.async_api import async_playwright

async def test_gr():
    print("Testing Goodreads scraper on Kensington fantasy book...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        scraper = GoodreadsScraper(headless=True)
        
        test_title = "The book of Azrael"
        test_author = "Amber V. Nicole"
        print(f"Searching: '{test_title}' by '{test_author}'...")
        res = await scraper.scrape_goodreads_data(context, test_title, test_author)
        print("Goodreads Result:")
        for k, v in (res or {}).items():
            print(f"  {k}: {v}")
            
        if res and res.get("Description"):
            sub = identify_romantasy_subgenre(res.get("Description"), res.get("Genre", ""))
            print(f"Identified Romantasy Subgenre: {sub}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_gr())

