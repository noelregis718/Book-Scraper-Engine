import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://randomhousebooks.com/imprint/del-rey/", wait_until="networkidle")
        
        # Click the Romance checkbox label
        await page.locator("label:has-text('Romance')").click()
        await page.wait_for_timeout(3000)
        
        while True:
            load_more = page.locator("button:has-text('Load More')").first
            if await load_more.is_visible():
                await load_more.scroll_into_view_if_needed()
                await load_more.click()
                await page.wait_for_timeout(3000)
            else:
                break
                
        books = await page.locator("article, .book-item").count()
        print(f"Total books under Romance: {books}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
