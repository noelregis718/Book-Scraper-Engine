import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.goodreads.com/book/show/10614.A_Court_of_Thorns_and_Roses", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        html = await page.content()
        with open("book_page.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
