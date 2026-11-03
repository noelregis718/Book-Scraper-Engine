import asyncio
import os
from playwright.async_api import async_playwright

async def click_turnstile():
    user_data_dir = os.path.abspath("backend/browser_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    async with async_playwright() as p:
        print("[1] Launching Chrome context...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ],
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.add_init_script("delete navigator.__proto__.webdriver;")
        
        url = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"
        print(f"[2] Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        for attempt in range(12):
            await asyncio.sleep(2.5)
            try:
                title = await page.title()
                print(f"[{attempt+1}] Title: '{title}'")
                if "just a moment" not in title.lower() and "attention required" not in title.lower():
                    print(">>> SUCCESS: Passed Turnstile!")
                    break
                    
                # Look for Cloudflare iframe
                for frame in page.frames:
                    if "challenges.cloudflare.com" in frame.url:
                        print("    Found Turnstile frame:", frame.url[:80])
                        # Try to find the checkbox or container
                        box = await frame.locator("body").bounding_box()
                        if box:
                            print(f"    Frame bounding box: {box}")
                            # Target the checkbox area on the left of Turnstile widget
                            # Usually Turnstile is ~300x65, checkbox is at x ~30, y ~32
                            target_x = box["x"] + 30
                            target_y = box["y"] + box["height"] / 2
                            print(f"    Clicking at ({target_x}, {target_y})...")
                            await page.mouse.click(target_x, target_y)
            except Exception as e:
                print(f"    Notice: {e}")
                
        # Wait a moment to see if navigation occurs
        await asyncio.sleep(4)
        try:
            print("Post-click Title:", await page.title())
            print("Post-click URL:  ", page.url)
            if "fantasy-fiction" in page.url and "just a moment" not in (await page.title()).lower():
                content = await page.content()
                with open("backend/kensington_page_success.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print(">>> Saved page content to backend/kensington_page_success.html!")
        except Exception as e:
            print("Post-click check notice:", e)
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(click_turnstile())
