import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        page = await context.new_page()
        
        print("Opening browser! Please solve any Cloudflare challenges.")
        await page.goto('https://www.panmacmillan.com.au/book-shop/?category%5B%5D=624')
        
        # Give user time to bypass captcha and page to fully render
        print("Waiting 15 seconds for you to bypass any security and for the page to load...")
        await asyncio.sleep(15)
        
        # Scroll down to make sure images/lazy elements load
        print("Scrolling down the page...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(5)
        
        html = await page.content()
        
        dump_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "panmac_dump.html")
        with open(dump_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"Page HTML successfully saved to {dump_path}!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
