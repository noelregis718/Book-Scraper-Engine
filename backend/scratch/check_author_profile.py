import asyncio
from playwright.async_api import async_playwright

async def check_profile():
    url = "https://www.kensingtonbooks.com/authors/allyson-k-abbott?v=13b5bfe96f3e"
    print(f"Navigating to author profile: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            print(f"Status code: {response.status}")
            title = await page.title()
            print(f"Page Title: '{title}'")
            
            # Print body text size or snippet
            body_text = await page.evaluate("() => document.body.innerText")
            print(f"Total text length: {len(body_text)}")
            print("First 1000 characters of page:")
            print(body_text[:1000])
            
            # Search for books
            links = await page.query_selector_all("a")
            print(f"Total links: {len(links)}")
            
        except Exception as e:
            print(f"Failed to load profile: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_profile())
