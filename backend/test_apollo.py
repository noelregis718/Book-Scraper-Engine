import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://www.sourcebooks.com/fiction/romance", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        state = await page.evaluate("window.__APOLLO_STATE__")
        if state:
            print("FOUND APOLLO STATE!")
            with open("e:/Internship/PocketFM/backend/apollo.json", "w", encoding="utf-8") as f:
                json.dump(state, f)
        else:
            print("NO APOLLO STATE FOUND.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
