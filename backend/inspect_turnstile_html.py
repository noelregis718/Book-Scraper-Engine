import asyncio
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
TARGET_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"

async def inspect_cf_frame():
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
        await asyncio.sleep(4)
        
        for f in page.frames:
            if "challenges.cloudflare.com" in f.url:
                print("Found Turnstile frame!")
                content = await f.content()
                print("Turnstile frame content:")
                print(content[:1500])
                
        await context.close()

if __name__ == "__main__":
    asyncio.run(inspect_cf_frame())

