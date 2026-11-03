import asyncio
import subprocess
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
TARGET_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"

async def inspect_page_html():
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
            
            # Wait until title is loaded
            for _ in range(15):
                t = await page.title()
                if "Fantasy Archives" in t:
                    break
                await asyncio.sleep(1)
                
            print("=== 3. PAGINATION INSPECTION ===")
            pag_container = await page.query_selector("nav.woocommerce-pagination, .woocommerce-pagination")
            if pag_container:
                pag_html = await pag_container.evaluate("el => el.outerHTML")
                safe_html = pag_html.encode('ascii', errors='replace').decode()
                print(safe_html)
                
            print("\n=== 4. TESTING DIRECT URL PAGINATION ===")
            for test_page in [1, 2, 3, 4, 5, 6]:
                page_url = f"https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/page/{test_page}/" if test_page > 1 else TARGET_URL
                print(f"Navigating to Page {test_page}: {page_url}...")
                await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
                products = await page.query_selector_all("li.product")
                
                # Sample 2 books on this page
                samples = []
                for p_item in products[:2]:
                    t_elem = await p_item.query_selector(".woocommerce-loop-product__title, h2")
                    a_elem = await p_item.query_selector(".single-author, span[class*='author']")
                    t = (await t_elem.inner_text()).strip() if t_elem else "N/A"
                    a = (await a_elem.inner_text()).strip() if a_elem else "N/A"
                    samples.append(f"'{t}' by {a}")
                    
                print(f"  Page {test_page}: {len(products)} books | Sample: {', '.join(samples)}")
                
            await browser.close()
        finally:
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(inspect_page_html())
