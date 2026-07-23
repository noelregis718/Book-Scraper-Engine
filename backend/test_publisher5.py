import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://www.goodreads.com/book/show/243114685-rejected-mate"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        
        # Click the "Book details" button to expand the publisher info if it exists
        try:
            # Often it's a button with text "Book details"
            await page.click('button:has-text("Book details")', timeout=5000)
            await asyncio.sleep(1)
        except Exception as e:
            pass
            
        content = await page.content()
        
        # Regex to look for "Published X by Y" or "Published by Y"
        matches = re.findall(r'Published.*?by\s+([^<]{3,30})', content)
        if matches:
            print(f"Found matches: {set(matches)}")
        else:
            print("No matches found using regex.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
