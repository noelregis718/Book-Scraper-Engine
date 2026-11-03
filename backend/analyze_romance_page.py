import asyncio
import subprocess
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
TARGET_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/romance/"

async def analyze_romance_page():
    print(f"Launching Chrome for Romance category: {TARGET_URL}")
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
            
            # Wait for clearance
            for i in range(15):
                t = await page.title()
                if "Romance" in t or "Archives" in t:
                    print(f"Loaded title: {t}")
                    break
                await asyncio.sleep(1)
                
            final_title = await page.title()
            print(f"Final Page Title: {final_title}")
            print(f"Final URL: {page.url}")
            
            # Result count
            res_count_el = await page.query_selector(".woocommerce-result-count")
            if res_count_el:
                res_text = (await res_count_el.inner_text()).strip()
                print(f"Result count text: {res_text}")
                
            # Product cards
            products = await page.query_selector_all("li.product")
            print(f"Products on Page 1: {len(products)}")
            
            # Pagination
            pag_elems = await page.query_selector_all(".page-numbers:not(.next):not(.prev)")
            page_numbers = []
            for el in pag_elems:
                text = (await el.inner_text()).strip()
                if text.isdigit():
                    page_numbers.append(int(text))
            print(f"Max page in pagination: {max(page_numbers) if page_numbers else 1}")
            
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
    asyncio.run(analyze_romance_page())

