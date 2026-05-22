import sys
import asyncio
sys.path.append('e:\\Internship\\PocketFM\\backend')
from goodreads_scraper import GoodreadsScraper
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        scraper = GoodreadsScraper()
        res = await scraper.search_author_books_with_links(page, 'Kristen Ciccarelli', 3)
        print("Result:", res)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
