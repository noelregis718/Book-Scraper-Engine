import asyncio
from playwright.async_api import async_playwright

async def debug_kensington():
    url = "https://www.kensingtonbooks.com/authors/allyson-k-abbott?v=13b5bfe96f3e"
    async with async_playwright() as p:
        print("[System] Launching browser to debug author page layout...")
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await page.add_init_script("delete navigator.__proto__.webdriver;")
        
        print(f"[System] Navigating to {url}...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            print("\n" + "!" * 60)
            print("  CLOUD FLARE BYPASS REQUIRED FOR DEBUGGING!")
            print("  Please check the box in the browser window if prompted.")
            print("!" * 60 + "\n")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, input, "Press [Enter] once the author profile page is fully loaded...")
            
            # Print page title
            title = await page.title()
            print(f"Page Title: '{title}'")
            
            # Let's inspect headings
            headings = await page.evaluate("""() => {
                const results = [];
                document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
                    results.push({tag: h.tagName, text: h.innerText.strip()});
                });
                return results;
            }""")
            print("\nFound headings on page:")
            for h in headings:
                print(f"  {h['tag']}: '{h['text']}'")
                
            # Let's inspect links that look like books
            book_links = await page.evaluate("""() => {
                const list = [];
                document.querySelectorAll('a').forEach(a => {
                    const href = a.getAttribute('href');
                    const text = a.innerText.strip();
                    if (href && href.includes('/books/')) {
                        list.push({text: text, href: href});
                    }
                });
                return list;
            }""")
            print(f"\nFound {len(book_links)} links containing '/books/':")
            for idx, bl in enumerate(book_links[:30], 1):
                print(f"  {idx}. '{bl['text']}' -> {bl['href']}")
                
        except Exception as e:
            print(f"[Error] Failed: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_kensington())
