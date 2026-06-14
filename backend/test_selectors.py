import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://www.sourcebooks.com/fiction/romance", wait_until="domcontentloaded")
        await asyncio.sleep(8)  # wait for react to render
        
        # dump the whole body to see what classes are used
        items = await page.query_selector_all('[class*="product-item"], [class*="item"], [class*="product"]')
        for item in items[:5]:
            html = await item.inner_html()
            if "href" in html and "<img" in html:
                print("FOUND POTENTIAL PRODUCT ITEM:")
                print(html[:500])
                print("---")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
