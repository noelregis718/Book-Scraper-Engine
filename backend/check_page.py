import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://knightagency.net/ourbooks/?product_cat=paranormalromance")
        await asyncio.sleep(5)
        
        # print all class names of li and div
        elements = await page.query_selector_all('li, div')
        classes = set()
        for el in elements:
            cls = await el.get_attribute('class')
            if cls and 'product' in cls:
                classes.add(cls)
                
        print("Classes containing 'product':", classes)
        
        # print some titles
        titles = await page.query_selector_all('h2, h3, .title, .product-title')
        print(f"Found {len(titles)} potential titles:")
        for t in titles[:5]:
            print(await t.inner_text())
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
