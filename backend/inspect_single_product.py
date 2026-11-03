import asyncio
import subprocess
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
SAMPLE_PRODUCT_URL = "https://www.kensingtonbooks.com/shop/the-changeling-queen-deluxe-stenciled-edges-9781645661740/"

async def inspect_single_product():
    proc = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={USER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
        SAMPLE_PRODUCT_URL
    ])
    await asyncio.sleep(4)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            page = browser.contexts[0].pages[0]
            
            # Wait for title
            for _ in range(15):
                t = await page.title()
                if "Just a moment" not in t:
                    break
                await asyncio.sleep(1)
                
            print(f"Product Page Title: {await page.title()}")
            
            # Product details
            title = await page.query_selector("h1.product_title, h1.entry-title")
            print(f"Title: {await title.inner_text() if title else 'N/A'}")
            
            author = await page.query_selector(".author, .by-author, .p-author, a[href*='/author/']")
            print(f"Author: {await author.inner_text() if author else 'N/A'}")
            
            price = await page.query_selector("p.price, .woocommerce-Price-amount")
            print(f"Price: {await price.inner_text() if price else 'N/A'}")
            
            # Book specifications table (ISBN, pub date, pages, etc.)
            spec_rows = await page.query_selector_all(".product_meta > span, .woocommerce-product-attributes tr, .book-details li, table.shop_attributes tr")
            print(f"Specifications rows found: {len(spec_rows)}")
            for r in spec_rows:
                print(f"  - {(await r.inner_text()).strip().replace(chr(10), ' : ')}")
                
            # Synopsis / Description
            desc = await page.query_selector("#tab-description, .woocommerce-product-details__short-description, .product-description")
            if desc:
                d_text = (await desc.inner_text()).strip()
                print(f"Synopsis ({len(d_text)} chars): {d_text[:200]}...")
                
            await browser.close()
        finally:
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(inspect_single_product())

