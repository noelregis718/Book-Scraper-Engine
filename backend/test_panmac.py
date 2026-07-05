import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        page = await context.new_page()
        print("Navigating to Pan Macmillan...")
        await page.goto('https://www.panmacmillan.com.au/book-shop/?category%5B%5D=624', wait_until='domcontentloaded')
        
        # Wait a bit for Cloudflare or JS to load
        await asyncio.sleep(5)
        
        # Look for typical product elements
        products = await page.query_selector_all('li.product, .book-item, article, .item, .book, div.product')
        print(f"Found {len(products)} potential products")
        
        if products:
            html = await products[0].inner_html()
            print("First product HTML:")
            print(html[:1500])
        else:
            print("No products found, printing page body:")
            print((await page.inner_text('body'))[:1000])
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
