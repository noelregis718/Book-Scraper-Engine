import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://randomhousebooks.com/imprint/del-rey/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        await page.screenshot(path="del_rey_screenshot.png", full_page=True)
        print("Screenshot saved to del_rey_screenshot.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
