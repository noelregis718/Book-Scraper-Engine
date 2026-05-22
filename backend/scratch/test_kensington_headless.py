import asyncio
import os
from playwright.async_api import async_playwright

async def test_kensington():
    url = "https://www.kensingtonbooks.com/authors/?v=13b5bfe96f3e#a"
    async with async_playwright() as p:
        print("[System] Launching Playwright browser with Google Chrome and Stealth args...")
        try:
            browser = await p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--disable-blink-features=AutomationControlled"]
            )
        except Exception as e:
            print(f"[System] Chrome channel launch failed, trying regular Chromium with stealth args: {e}")
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        # Additional javascript to remove the webdriver property just in case
        await page.add_init_script("delete navigator.__proto__.webdriver;")
        
        print(f"[System] Navigating to {url}...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            print("[System] Sleeping for 20 seconds to allow Turnstile challenge to be bypassed...")
            await asyncio.sleep(20)
            
            # Let's check the title
            title = await page.title()
            print(f"[System] Page Title now: '{title}'")
            
            # Check all links
            links = await page.query_selector_all("a")
            print(f"[System] Total links found: {len(links)}")
            
            author_names = []
            for link in links:
                href = await link.evaluate("el => el.getAttribute('href')")
                text = (await link.inner_text()).strip()
                if href and ("/author/" in href.lower() or "author" in href.lower()):
                    if text and text not in author_names and len(text) < 50:
                        # Exclude navigation/footer links containing 'author'
                        if "about" not in text.lower() and "contact" not in text.lower() and "submission" not in text.lower() and "faq" not in text.lower() and "home" not in text.lower() and "books" not in text.lower():
                            author_names.append(text)
                            
            print(f"[System] Found {len(author_names)} filtered author names:")
            for name in sorted(author_names)[:30]:
                print(f"  - '{name}'")
                
        except Exception as e:
            print(f"[Error] Failed: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_kensington())
