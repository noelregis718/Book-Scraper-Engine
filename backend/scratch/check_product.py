import asyncio
from playwright.async_api import async_playwright

async def check_product_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://knightagency.net/product/everyday-witchs-book-deities-ancient-gods-modern-pagans-deborah-blake/"
        print(f"Opening {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        content = await page.content()
        with open("product_source.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Product source saved.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_product_page())
