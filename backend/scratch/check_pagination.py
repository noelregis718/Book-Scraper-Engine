import asyncio
from playwright.async_api import async_playwright

async def check_pagination():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://knightagency.net/ourbooks/?product_cat=romantic-suspense"
        print(f"Opening {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        # Check for pagination links
        next_btn = await page.query_selector('.next.page-numbers')
        if next_btn:
            print("Found Next button.")
        else:
            print("No Next button found.")
            
        page_numbers = await page.query_selector_all('.page-numbers')
        print(f"Found {len(page_numbers)} page number elements.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_pagination())
