import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://www.amazon.com/s?k=Paranormal+Romance&i=stripbooks&page=1')
        title = await page.title()
        print(f"PAGE TITLE: {title}")
        items = await page.query_selector_all('[data-asin]')
        print(f"ASIN COUNT: {len(items)}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
