import asyncio
import subprocess
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
TARGET_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"

async def check_total_pages():
    proc = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={USER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
        TARGET_URL
    ])
    await asyncio.sleep(4)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            page = browser.contexts[0].pages[0]
            
            # Wait for title
            for _ in range(15):
                if "Fantasy Archives" in await page.title():
                    break
                await asyncio.sleep(1)
                
            # Get pagination items
            pag_elems = await page.query_selector_all(".page-numbers:not(.next):not(.prev)")
            page_numbers = []
            for el in pag_elems:
                text = (await el.inner_text()).strip()
                if text.isdigit():
                    page_numbers.append(int(text))
                    
            print(f"Max page found in pagination: {max(page_numbers) if page_numbers else 1}")
            
            # Check result count text (e.g. "Showing 1-60 of 250 results")
            result_count = await page.query_selector(".woocommerce-result-count")
            if result_count:
                print(f"Result count text: {await result_count.inner_text()}")
                
            await browser.close()
        finally:
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(check_total_pages())

