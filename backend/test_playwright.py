import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://www.goodreads.com/book/show/6211756-the-cold-light-of-mourning', wait_until='domcontentloaded')
        html = await page.content()
        with open('book_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
