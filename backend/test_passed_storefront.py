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
    
    await asyncio.sleep(4)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            
            # Find the kensington tab
            page = None
            for p_elem in context.pages:
                if "kensingtonbooks.com" in p_elem.url:
                    page = p_elem
                    break
            if not page:
                page = context.pages[0]
                
            print(f"Attached to page: {page.url}")
            
            # Wait for navigation / clearance
            print("Waiting for page load after Cloudflare redirect...")
            for i in range(25):
                try:
                    title = await page.title()
                    url = page.url
                    print(f"[{i+1}s] Title: '{title}' | URL: {url}")
                    if "Just a moment" not in title and "Checking" not in title and len(title) > 0:
                        print("\n>>> CLOUDFLARE BYPASSED! PAGE LOADED! <<<")
                        break
                except Exception as ex:
                    print(f"[{i+1}s] Navigating / Redirecting... ({ex})")
                await asyncio.sleep(1.5)
                
            # Now let's extract the page structure
            print("\n================== DOM ANALYSIS ==================")
            await page.wait_for_load_state("networkidle", timeout=15000)
            
            final_title = await page.title()
            print(f"Final Page Title: {final_title}")
            print(f"Final URL: {page.url}")
            
            # Product card selector inspection
            selectors = [
                "li.product",
                ".product",
                ".type-product",
                "article.product",
                ".products li"
            ]
            for sel in selectors:
                elements = await page.query_selector_all(sel)
                print(f"Selector '{sel}': {len(elements)} found")
                
            # Test extraction on the first 5 books
            products = await page.query_selector_all("li.product, .type-product")
            print(f"\nExtracting from {len(products)} products on Page 1:")
            
            for idx, p_elem in enumerate(products[:10], 1):
                # Title
                t_elem = await p_elem.query_selector("h2, h3, .woocommerce-loop-product__title")
                title_text = (await t_elem.inner_text()).strip() if t_elem else "N/A"
                
                # Link
                link_elem = await p_elem.query_selector("a")
                link_url = await link_elem.get_attribute("href") if link_elem else "N/A"
                
                # Author
                # Let's inspect all text or specific author classes
                all_text = (await p_elem.inner_text()).strip().split("\n")
                
                # Image
                img_elem = await p_elem.query_selector("img")
                img_src = await img_elem.get_attribute("src") if img_elem else "N/A"
                
                print(f"{idx}. Title: {title_text}")
                print(f"   Lines: {all_text}")
                print(f"   URL: {link_url}")
                print(f"   Image: {img_src[:60]}...")
                print("-" * 50)
                
            # Check pagination structure
            print("\n================== PAGINATION ==================")
            pag_links = await page.query_selector_all(".page-numbers a, nav.woocommerce-pagination a")
            print(f"Pagination links found: {len(pag_links)}")
            for pl in pag_links:
                t = await pl.inner_text()
                href = await pl.get_attribute("href")
                print(f"  Page Link '{t}': {href}")
                
            await browser.close()
        except Exception as e:
            print(f"Error during analysis: {e}")
        finally:
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(analyze_storefront())

