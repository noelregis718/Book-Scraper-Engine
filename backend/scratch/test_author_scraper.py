import asyncio
from playwright.async_api import async_playwright
from scraper import AuthorScraper

async def test_author():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = AuthorScraper()
        
        # Test with a known author
        author = "Sarah J. Maas"
        print(f"Testing for author: {author}")
        details = await scraper.find_author_details(context, author)
        print(f"Details found: {details}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_author())
