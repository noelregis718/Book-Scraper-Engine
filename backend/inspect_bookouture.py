import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Visiting Bookouture...")
        await page.goto("https://bookouture.com/books/?genre=romance", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # See if there's a load more button
        load_more = await page.query_selector("button:has-text('Load More'), .load-more, .ajax-load-more")
        print(f"Load more button found: {load_more is not None}")
        
        # Get the first few items
        print("\nExtracting HTML of first item...")
        items = await page.query_selector_all(".book, .product, article, .item, .book-item")
        if not items:
            print("No generic items found. Dumping first 1000 chars of body...")
            body = await page.evaluate("document.body.innerHTML")
            print(body[:1000])
        else:
            print(f"Found {len(items)} items.")
            first_html = await items[0].evaluate("el => el.innerHTML")
            print(first_html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
