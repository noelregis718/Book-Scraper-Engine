import asyncio
from playwright.async_api import async_playwright
from scraper import AuthorScraper

async def test_authors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = AuthorScraper()
        
        authors = ["Sarah J. Maas", "Rebecca Yarros", "Carissa Broadbent", "Jennifer L. Armentrout"]
        
        for author in authors:
            print(f"\n--- Testing for author: {author} ---")
            details = await scraper.find_author_details(context, author)
            print(f"Details found: {details}")
            await asyncio.sleep(2) # Delay between authors
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_authors())
