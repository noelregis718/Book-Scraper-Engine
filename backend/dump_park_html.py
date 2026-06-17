import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://parkfinebrower.com/authors/", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5)
        
        html = await page.content()
        with open("park_authors.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
