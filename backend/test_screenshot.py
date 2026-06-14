import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        try:
            await page.goto("https://www.sourcebooks.com/fiction/romance", wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print("Goto timeout:", e)
        await asyncio.sleep(5)
        await page.screenshot(path="e:/Internship/PocketFM/screenshot.png")
        html = await page.content()
        with open("e:/Internship/PocketFM/page.html", "w", encoding="utf-8") as f:
            f.write(html)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
