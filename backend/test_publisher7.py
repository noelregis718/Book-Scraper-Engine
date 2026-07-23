import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://www.goodreads.com/book/show/243114685-rejected-mate"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        script = await page.query_selector('#__NEXT_DATA__')
        if script:
            content = await script.inner_text()
            data = json.loads(content)
            
            # apollo state
            apollo = data.get('props', {}).get('pageProps', {}).get('apolloState', {})
            for key, val in apollo.items():
                if isinstance(val, dict) and 'publisher' in val:
                    print("Found publisher:", val['publisher'])
                if isinstance(val, dict) and val.get('__typename') == 'Work':
                    details = val.get('details')
                    if details and isinstance(details, dict) and 'publisher' in details:
                        print("Found details publisher:", details['publisher'])
                        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
