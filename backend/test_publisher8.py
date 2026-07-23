import asyncio
import json
from playwright.async_api import async_playwright
import re

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
            
            apollo = data.get('props', {}).get('pageProps', {}).get('apolloState', {})
            # Look for any string containing the word "publisher" or "publish"
            for k, v in apollo.items():
                s = json.dumps(v).lower()
                if 'publish' in s:
                    print(f"Key: {k}")
                    if isinstance(v, dict):
                        for subk, subv in v.items():
                            if 'publish' in str(subv).lower() or 'publish' in subk.lower():
                                print(f"  {subk}: {subv}")
                                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
