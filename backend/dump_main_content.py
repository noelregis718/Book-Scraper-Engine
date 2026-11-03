import asyncio
import subprocess
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
SAMPLE_PRODUCT_URL = "https://www.kensingtonbooks.com/shop/the-changeling-queen-deluxe-stenciled-edges-9781645661740/"

async def dump_main_content():
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
            
            main_info = await page.evaluate("""() => {
                const main = document.querySelector('main, #main, #content, .site-main, .entry-content');
                if (!main) return 'No main found';
                return {
                    h1: Array.from(main.querySelectorAll('h1')).map(e => e.innerText),
                    h2: Array.from(main.querySelectorAll('h2')).map(e => e.innerText),
                    p: Array.from(main.querySelectorAll('p')).map(e => e.innerText.trim()).filter(t => t.length > 20).slice(0, 5),
                    text: main.innerText.slice(0, 1500)
                };
            }""")
            print("Main container content:")
            print(main_info)
                
            await browser.close()
        finally:
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(dump_main_content())

