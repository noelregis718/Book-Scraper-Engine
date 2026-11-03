import asyncio
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
TARGET_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"

async def inspect_cf():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=r"E:\Internship\PocketFM\backend\browser_profile",
            executable_path=CHROME_PATH,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
        
        print("Looking for iframes and Cloudflare widgets...")
        await asyncio.sleep(4)
        
        frames = page.frames
        print(f"Total frames: {len(frames)}")
        for i, f in enumerate(frames):
            print(f"Frame {i}: {f.url}")
            
        # Check for challenge container
        selectors = [
            "iframe[src*='challenges.cloudflare.com']",
            "div#challenge-stage",
            "div.cf-turnstile-wrapper",
            "input[type='checkbox']"
        ]
        for sel in selectors:
            elem = await page.query_selector(sel)
            print(f"Selector '{sel}': {'FOUND' if elem else 'NOT FOUND'}")
            
        # If cloudflare iframe found, let's see inside
        cf_frame = None
        for f in frames:
            if "challenges.cloudflare.com" in f.url:
                cf_frame = f
                break
                
        if cf_frame:
            print("Found Cloudflare frame! Checking elements inside frame...")
            try:
                checkbox = await cf_frame.query_selector("input[type='checkbox'], span.mark, div.ctp-checkbox-label, .ctp-checkbox-container")
                print(f"Checkbox inside CF frame: {'FOUND' if checkbox else 'NOT FOUND'}")
                if checkbox:
                    print("Attempting to click Cloudflare checkbox...")
                    box = await checkbox.bounding_box()
                    if box:
                        await page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                        print("Clicked Cloudflare checkbox via mouse coordinates!")
                        await asyncio.sleep(6)
                        print(f"New title after click: {await page.title()}")
                        print(f"New URL after click: {page.url}")
            except Exception as e:
                print(f"Error inspecting/clicking CF frame: {e}")
                
        # Also check page title
        print(f"Final Page Title: {await page.title()}")
        await context.close()

if __name__ == "__main__":
    asyncio.run(inspect_cf())

