import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://www.goodreads.com/book/show/243114685-rejected-mate"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        content = await page.content()
        
        # Look for JSON embedded state
        # The apollo state often contains "Publisher":{"name":"Something"}
        match1 = re.search(r'"publisher"\s*:\s*"?([^"}]+)"?', content, re.IGNORECASE)
        match2 = re.search(r'"Publisher"\s*:\s*\{\s*"name"\s*:\s*"([^"]+)"', content)
        match3 = re.search(r'publisher(?:Name)?["\']?.*?:\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
        
        print(f"Match 1: {match1.group(1) if match1 else 'None'}")
        print(f"Match 2: {match2.group(1) if match2 else 'None'}")
        print(f"Match 3: {match3.group(1) if match3 else 'None'}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
