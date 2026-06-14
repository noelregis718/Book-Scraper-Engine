import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        requests_seen = []
        page.on("request", lambda r: requests_seen.append(r.url) if 'graphql' in r.url or 'api' in r.url else None)
        
        await page.goto("https://www.sourcebooks.com/fiction/romance")
        await asyncio.sleep(8)
        
        with open("e:/Internship/PocketFM/backend/api_calls.txt", "w") as f:
            f.write("\n".join(requests_seen))
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
