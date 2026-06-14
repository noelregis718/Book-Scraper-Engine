import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        async def handle_response(response):
            if 'graphql' in response.url:
                try:
                    text = await response.text()
                    data = json.loads(text)
                    if 'data' in data and 'products' in data['data']:
                        items = data['data']['products'].get('items', [])
                        if len(items) > 0:
                            print(f"FOUND PRODUCTS WITH {len(items)} ITEMS!")
                            with open("e:/Internship/PocketFM/backend/products_actual.json", "w", encoding="utf-8") as f:
                                json.dump(data, f)
                except Exception as e:
                    pass
                    
        page.on("response", handle_response)
        
        print("Navigating...")
        await page.goto("https://www.sourcebooks.com/fiction/romance?p=2", wait_until="domcontentloaded")
        await asyncio.sleep(8)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
