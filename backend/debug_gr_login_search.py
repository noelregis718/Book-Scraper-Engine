import asyncio
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

async def test():
    scraper = GoodreadsScraper(headless=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. Login
        print("Logging in...")
        await scraper.login_to_goodreads(page)
        
        # 2. Search
        query = "Wild Love Lauren Accardo"
        print(f"Searching for: {query}")
        await page.goto(f"https://www.goodreads.com/search?q={query.replace(' ', '+')}")
        await asyncio.sleep(5)
        
        results = await page.query_selector_all('a.bookTitle')
        print(f"Found {len(results)} books after login.")
        for r in results[:5]:
            print(f"  - {await r.inner_text()} ({await r.get_attribute('href')})")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
