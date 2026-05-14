import asyncio
from playwright.async_api import async_playwright

async def dump():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        page = await context.new_page()
        print("Navigating...")
        await page.goto('https://knightagency.net/ourbooks/?product_cat=romantic-suspense', wait_until='domcontentloaded')
        await asyncio.sleep(5)
        
        products = await page.query_selector_all('.product')
        if products:
            print(f"Found {len(products)} products.")
            html = await products[0].inner_html()
            print("--- HTML START ---")
            print(html)
            print("--- HTML END ---")
        else:
            print("No products found.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump())
