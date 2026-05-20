import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.psliterary.com/fiction/", wait_until="networkidle", timeout=60000)
        
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(5)
        
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        with open("page_text.txt", "w", encoding="utf-8") as f:
            f.write(soup.get_text(separator="\n", strip=True))
            
        await browser.close()
        print("Text saved to page_text.txt")

asyncio.run(inspect())
