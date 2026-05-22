import asyncio
from playwright.async_api import async_playwright

async def check_authors_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://knightagency.net/our-authors/"
        print(f"Opening {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(5)
        content = await page.content()
        with open("authors_source.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Authors source saved.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_authors_page())
