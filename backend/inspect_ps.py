import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.psliterary.com/fiction/", wait_until="networkidle", timeout=60000)
        
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(5)
        
        html = await page.content()
        with open("full_dom.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()
        print("HTML saved to full_dom.html")

asyncio.run(inspect())
