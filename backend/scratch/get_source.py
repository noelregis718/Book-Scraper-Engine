import asyncio
from playwright.async_api import async_playwright

async def check_knight_agency():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://knightagency.net/ourbooks/?product_cat=fantasy-romance"
        print(f"Opening {url}...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)
            content = await page.content()
            with open("knight_agency_source.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Source saved to knight_agency_source.html")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_knight_agency())
