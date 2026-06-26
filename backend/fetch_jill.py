import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://jillgrinbergliterary.com/authors/', wait_until='networkidle')
        html = await page.content()
        with open('jill_rendered.html', 'w', encoding='utf-8') as f:
            f.write(html)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
