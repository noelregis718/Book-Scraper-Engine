import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://www.goodreads.com/book/show/243114685-rejected-mate"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        
        scripts = await page.query_selector_all('script[type="application/ld+json"]')
        for s in scripts:
            content = await s.inner_text()
            try:
                data = json.loads(content)
                if '@type' in data and data['@type'] == 'Book':
                    print("Found Book schema!")
                    if 'publisher' in data:
                        print("Publisher:", data['publisher'])
                    else:
                        print("No publisher in schema.")
            except Exception as e:
                pass
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
