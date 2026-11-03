import asyncio
from playwright.async_api import async_playwright

async def scan():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await page.add_init_script("delete navigator.__proto__.webdriver;")
        url = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"
        print(f"[Scan] Navigating to {url} with domcontentloaded...")
        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(3)
            title = await page.title()
            print(f"[Scan] Page title: {title}")
            content = await page.content()
            print(f"[Scan] Content length: {len(content)}")
            
            # Save snippet of content
            with open("backend/sample_page.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("[Scan] Saved sample_page.html")
            
        except Exception as e:
            print(f"[Scan] Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scan())

