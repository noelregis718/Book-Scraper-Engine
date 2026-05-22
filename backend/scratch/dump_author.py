import asyncio
from playwright.async_api import async_playwright

async def dump_author_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.limaagency.se/authors/fiction/anna-alemo", wait_until="networkidle")
        content = await page.content()
        with open("anna_alemo.html", "w", encoding="utf-8") as f:
            f.write(content)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump_author_page())
