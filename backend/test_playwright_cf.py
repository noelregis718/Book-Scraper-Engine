import asyncio
import os
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"E:\Internship\PocketFM\backend\browser_profile"
TARGET_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"

async def test_playwright():
    print(f"Launching Playwright with real Chrome at: {CHROME_PATH}")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            executable_path=CHROME_PATH,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--start-maximized"
            ],
            viewport=None,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Anti-detect script
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        print(f"Navigating to {TARGET_URL}...")
        try:
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"Navigation warning: {e}")
            
        print("Waiting 10 seconds to observe Cloudflare resolution...")
        await asyncio.sleep(10)
        
        title = await page.title()
        url = page.url
        print(f"Page Title: {title}")
        print(f"Current URL: {url}")
        
        # Check if products exist on page
        products = await page.query_selector_all(".product, li.product, article.product, div.product-inner")
        print(f"Products found on page: {len(products)}")
        
        if len(products) > 0:
            for i in range(min(5, len(products))):
                text = await products[i].inner_text()
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                print(f"  Product {i+1}: {lines[:2]}")
        else:
            # Let's inspect HTML snippet
            content = await page.content()
            if "Just a moment" in content:
                print("STILL on Cloudflare 'Just a moment' challenge page.")
            else:
                print("Page content length:", len(content))
                print("Preview:", content[:300])
                
        await context.close()

if __name__ == "__main__":
    asyncio.run(test_playwright())

