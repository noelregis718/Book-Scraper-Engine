import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://www.goodreads.com/book/show/224063672-alpha-king-s-secret-baby"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        content = await page.content()
        match = re.search(r'(\d+)\s*pages', content, re.IGNORECASE)
        if match:
            print("Found via regex:", match.group(1))
        else:
            print("Regex failed.")
            
        page_format_el = await page.query_selector('[data-testid="pagesFormat"]')
        if page_format_el:
            print("Found via testid:", await page_format_el.inner_text())
        else:
            print("Testid failed.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
