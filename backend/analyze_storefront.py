import asyncio
import subprocess
import time
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
TARGET_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"

async def analyze_storefront():
    print("Launching Native Chrome...")
    proc = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={USER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
        TARGET_URL
    ])
    
    print("Connecting Playwright over CDP...")
    await asyncio.sleep(3)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            contexts = browser.contexts
            context = contexts[0]
            
            # Find the kensington tab
            page = None
            for p_elem in context.pages:
                if "kensingtonbooks.com" in p_elem.url:
                    page = p_elem
                    break
            if not page:
                page = context.pages[0]
                
            print(f"Attached to page: {page.url} | Title: {await page.title()}")
            
            # Wait for user or auto-bypass (up to 20s)
            print("Monitoring page title for Cloudflare clearance...")
            for i in range(20):
                title = await page.title()
                print(f"[{i+1}s] Page Title: {title} | URL: {page.url}")
                if "Just a moment" not in title and "Checking" not in title:
                    print("\n>>> SUCCESS: CLOUDFLARE BYPASSED! <<<")
                    break
                await asyncio.sleep(1)
                
            # If still on challenge, let's look for any interactive element or iframe
            current_title = await page.title()
            if "Just a moment" in current_title:
                print("Still on challenge page. Let's inspect the page content...")
            else:
                print("\n================== DOM ANALYSIS ==================")
                # Extract structure
                product_cards = await page.query_selector_all("li.product, .product, div.product-card, article")
                print(f"Total product cards found: {len(product_cards)}")
                
                # Check pagination
                pagination = await page.query_selector_all(".woocommerce-pagination, .pagination, .page-numbers, nav.woocommerce-pagination")
                print(f"Pagination elements found: {len(pagination)}")
                if pagination:
                    pag_text = await pagination[0].inner_text()
                    print(f"Pagination text: {pag_text.replace(chr(10), ' ')}")
                    
                # Inspect first 3 books
                for idx, card in enumerate(product_cards[:3], 1):
                    text = await card.inner_text()
                    html = await card.inner_html()
                    print(f"\n--- Product Card {idx} ---")
                    print("Text snippet:", text.replace("\n", " | ")[:150])
                    
            await browser.close()
        except Exception as e:
            print(f"Error during analysis: {e}")
        finally:
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(analyze_storefront())

