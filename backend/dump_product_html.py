import asyncio
import subprocess
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
SAMPLE_PRODUCT_URL = "https://www.kensingtonbooks.com/shop/the-changeling-queen-deluxe-stenciled-edges-9781645661740/"

async def dump_product_elements():
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
            
            # Extract all headings and text blocks
            headings = await page.evaluate("""() => {
                const res = [];
                document.querySelectorAll('h1, h2, h3, h4, h5, p, span, a').forEach(el => {
                    const txt = el.innerText.trim();
                    const cls = el.className;
                    if (txt.length > 5 && txt.length < 150) {
                        res.push({ tag: el.tagName, class: cls, text: txt });
                    }
                });
                return res.slice(0, 30);
            }""")
            for h in headings:
                print(f"[{h['tag']}.{h['class'][:30]}] {h['text']}")
                
            await browser.close()
        finally:
            proc.terminate()

if __name__ == "__main__":
    asyncio.run(dump_product_elements())

