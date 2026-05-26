import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page()
        await page.goto('https://www.stormliteraryagency.com/authors.html', wait_until='networkidle')
        html = await page.content()
        with open('storm.html', 'w', encoding='utf-8') as f:
            f.write(html)
        await b.close()

asyncio.run(run())
