import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent='Mozilla/5.0')
        page = await context.new_page()
        
        await page.goto('https://harlequin.com/pages/romance-bestsellers', wait_until='networkidle')
        
        books = await page.query_selector_all('div.card-product')
        print(f"Initially found {len(books)} books.")
        
        # Scroll down several times to trigger infinite scroll
        for i in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
        books_after = await page.query_selector_all('div.card-product')
        print(f"After scrolling, found {len(books_after)} books.")
        
        # Check if there is a next/load more button
        load_more = await page.query_selector('text=Load More, text=Show More, text=Next')
        if load_more:
            print("Found a Load More / Next button!")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
