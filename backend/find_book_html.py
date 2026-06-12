import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://randomhousebooks.com/imprint/del-rey/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Let's get the container of books
        # Often it's a div with an ID like 'books' or 'archive' or 'results'
        # But we can just look for the first element containing 'Defy the Dusk' (a book I saw in the screenshot)
        book_element = page.locator("text='Defy the Dusk'").first
        if await book_element.count() > 0:
            parent = book_element.locator("xpath=ancestor::div[contains(@class, 'book') or contains(@class, 'grid') or contains(@class, 'item') or position()=4]").first
            html = await parent.evaluate("el => el.outerHTML")
            print("Book HTML:\n", html)
        else:
            print("Could not find 'Defy the Dusk'.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
