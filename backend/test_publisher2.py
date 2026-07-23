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
        
        # Look for "First published" or "Published" text
        details_el = await page.query_selector('.BookDetails')
        if details_el:
            text = await details_el.inner_text()
            print("BookDetails text:", text)
            
            # Usually it says something like: "First published October 28, 2021 by Publisher Name"
            match = re.search(r'Published\s+(?:.*?\s+)?by\s+(.+)', text)
            if match:
                print("Extracted Publisher:", match.group(1).strip())
        else:
            print("No BookDetails found.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
