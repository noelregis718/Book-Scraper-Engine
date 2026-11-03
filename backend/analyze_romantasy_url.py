import asyncio
import subprocess
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
TARGET_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/?yith_wcan=1&product_cat=fantasy-fiction+romance"

async def analyze_romantasy_url():
    print(f"Launching Chrome for Romantasy URL: {TARGET_URL}")
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
            for i in range(15):
                t = await page.title()
                if "Just a moment" not in t:
                    print(f"Clearance active: '{t}'")
                    break
                await asyncio.sleep(1)
                
            print(f"Page Title: {await page.title()}")
            print(f"Current URL: {page.url}")
            
            # Result count
            res_count = await page.query_selector(".woocommerce-result-count")
            if res_count:
                print(f"Result Count: {await res_count.inner_text()}")
                
            # Product cards
            products = await page.query_selector_all("li.product")
            print(f"Products on Page 1: {len(products)}")
            
            # Check pagination links
            pag_links = await page.query_selector_all(".page-numbers a, nav.woocommerce-pagination a")
            print(f"Pagination Links found: {len(pag_links)}")
            for pl in pag_links:
                t = await pl.inner_text()
                href = await pl.get_attribute("href")
                print(f"  Page link '{t}': {href}")
                
            # Sample first 3 books
            for idx, p_item in enumerate(products[:3], 1):
                t_el = await p_item.query_selector(".woocommerce-loop-product__title, h2")
                a_el = await p_item.query_selector(".single-author, span[class*='author']")
                t = (await t_el.inner_text()).strip() if t_el else "N/A"
                a = (await a_el.inner_text()).strip() if a_el else "N/A"
                print(f"  Sample {idx}: '{t}' by {a}")
                
            await browser.close()
        finally:
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(analyze_romantasy_url())

