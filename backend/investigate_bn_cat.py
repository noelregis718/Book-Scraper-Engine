import asyncio
from playwright.async_api import async_playwright
import re

async def investigate():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        url = "https://www.barnesandnoble.com/b/books/romance/fantasy-romance/_/N-29Z8q8Z1glz"
        print(f"Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)
            html = await page.content()
            
            with open("bn_cat_dump.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved DOM to bn_cat_dump.html")
            
        except Exception as e:
            print(f"Error: {e}")
            
        await browser.close()

asyncio.run(investigate())
