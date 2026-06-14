import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        bodies = []
        async def handle_request(req):
            if req.method == 'POST' and 'graphql' in req.url:
                try:
                    bodies.append(req.post_data)
                except:
                    pass
                    
        page.on("request", handle_request)
        await page.goto("https://www.sourcebooks.com/fiction/romance")
        await asyncio.sleep(5)
        
        with open("e:/Internship/PocketFM/backend/graphql_bodies.txt", "w", encoding="utf-8") as f:
            for b in bodies:
                if b: f.write(b + "\n---\n")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
