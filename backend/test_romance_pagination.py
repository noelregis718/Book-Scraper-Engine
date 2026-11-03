import asyncio
import subprocess
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"

async def test_romance_pagination():
    proc = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={USER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.kensingtonbooks.com/shop/product-category/fiction/romance/"
    ])
    await asyncio.sleep(4)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            page = browser.contexts[0].pages[0]
            
            for test_page in [1, 2, 20, 46]:
                url = "https://www.kensingtonbooks.com/shop/product-category/fiction/romance/" if test_page == 1 else f"https://www.kensingtonbooks.com/shop/product-category/fiction/romance/page/{test_page}/"
                print(f"Testing Page {test_page}: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
                
                products = await page.query_selector_all("li.product")
                t_el = await products[0].query_selector(".woocommerce-loop-product__title, h2") if products else None
                first_title = (await t_el.inner_text()).strip() if t_el else "N/A"
                print(f"  -> Page {test_page}: {len(products)} products found | First book: '{first_title}'")
                
            await browser.close()
        finally:
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(test_romance_pagination())

