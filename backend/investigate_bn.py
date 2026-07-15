import asyncio
from playwright.async_api import async_playwright

async def investigate():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        url = "https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance"
        print(f"Navigating to {url} ...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        print("Scrolling...")
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
            
        print("Taking screenshot...")
        await page.screenshot(path="bn_investigate.png", full_page=True)
        print("Saved to bn_investigate.png")
        await browser.close()

asyncio.run(investigate())
