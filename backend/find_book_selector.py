import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://randomhousebooks.com/imprint/del-rey/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # We need to find the book elements.
        # Let's find all images that look like book covers
        images = await page.locator("img").all()
        for img in images[:10]:
            src = await img.get_attribute("src")
            if 'book' in src or 'cover' in src or 'image' in src:
                # Get the parent link or container
                parent = img.locator("xpath=ancestor::a").first
                if await parent.count() > 0:
                    html = await parent.evaluate("el => el.outerHTML")
                    print("Book link HTML:\n", html)
                    break
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
