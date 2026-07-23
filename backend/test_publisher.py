import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://www.goodreads.com/book/show/243114685-rejected-mate"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        
        # Look for Publication Info
        pub_info = await page.query_selector('[data-testid="publicationInfo"]')
        if pub_info:
            text = await pub_info.inner_text()
            print(f"Publication Info found: {text}")
        else:
            print("No publication info found using new UI selector.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
