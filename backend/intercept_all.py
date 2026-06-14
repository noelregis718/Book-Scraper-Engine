import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        urls = []
        page.on("request", lambda r: urls.append(r.url))
        
        await page.goto("https://www.sourcebooks.com/fiction/romance")
        await asyncio.sleep(5)
        
        with open("e:/Internship/PocketFM/backend/all_urls.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(urls))
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
