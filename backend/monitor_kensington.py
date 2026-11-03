import asyncio
import os
from playwright.async_api import async_playwright

async def monitor():
    user_data_dir = os.path.abspath("backend/browser_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.add_init_script("delete navigator.__proto__.webdriver;")
        
        def on_nav(frame):
            if frame == page.main_frame:
                print(f"[NAVIGATED] Main frame -> {frame.url}")
        page.on("framenavigated", on_nav)
        
        url = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"
        print(f"[GOTO] {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"[GOTO ERROR] {e}")
            
        print("[MONITOR] Monitoring for 25 seconds...")
        for i in range(12):
            await asyncio.sleep(2)
            try:
                title = await page.title()
                print(f"[{i*2}s] URL: {page.url} | Title: '{title}'")
                if "just a moment" not in title.lower() and "attention required" not in title.lower():
                    print(">>> SUCCESS! Bypassed!")
                    content = await page.content()
                    with open("backend/kensington_page_success.html", "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Saved {len(content)} bytes to backend/kensington_page_success.html")
                    break
            except Exception as e:
                print(f"[{i*2}s] Exception checking title: {e}")
                
        await context.close()

if __name__ == "__main__":
    asyncio.run(monitor())

