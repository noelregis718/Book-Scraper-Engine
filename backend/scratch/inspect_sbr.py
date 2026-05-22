import asyncio
from playwright.async_api import async_playwright

async def inspect_author(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Scroll down multiple times to trigger dynamic loading
        print("Scrolling down...")
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1)
        
        # Dump content to check for books
        content = await page.content()
        with open("sbr_author_inspect.html", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("Page content dumped to sbr_author_inspect.html")
        await asyncio.sleep(5) # Give time to manually look if needed
        await browser.close()

if __name__ == "__main__":
    # Test with Abigail Davies
    asyncio.run(inspect_author("https://sbrmedia.com/authors/aleatha-romig/"))
