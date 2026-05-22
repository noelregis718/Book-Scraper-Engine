import asyncio
from playwright.async_api import async_playwright
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from goodreads_scraper import GoodreadsScraper

async def test():
    gs = GoodreadsScraper(headless=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        # Test Flowerheart
        res = await gs.scrape_goodreads_data(context, "Flowerheart", "Catherine Bakewell")
        print(f"\nFLOWERHEART RESULT: {res}")
        
        # Test Where Shadows Bloom
        res2 = await gs.scrape_goodreads_data(context, "Where Shadows Bloom", "Catherine Bakewell")
        print(f"\nWHERE SHADOWS BLOOM RESULT: {res2}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
