import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://randomhousebooks.com/imprint/del-rey/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Check all text on the page
        body_text = await page.inner_text("body")
        if "romantasy" in body_text.lower():
            print("FOUND romantasy in page text!")
            # Let's see where it is
            elements = await page.locator("text=Romantasy").all()
            print(f"Found {len(elements)} elements with exact text 'Romantasy'")
            for el in elements:
                html = await el.evaluate("node => node.outerHTML")
                print("HTML:", html)
            
            elements2 = await page.locator("text=/romantasy/i").all()
            print(f"Found {len(elements2)} elements with case-insensitive text 'romantasy'")
            for el in elements2:
                html = await el.evaluate("node => node.outerHTML")
                print("HTML:", html)
        else:
            print("Did not find romantasy in page body.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
