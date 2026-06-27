import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        try:
            print("Navigating to City Owl Press...")
            await page.goto("https://cityowlpress.com/collections/all", wait_until="networkidle", timeout=60000)
            
            # Wait for products to load
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            with open("cityowl_rendered.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Successfully fetched HTML and saved to cityowl_rendered.html")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
