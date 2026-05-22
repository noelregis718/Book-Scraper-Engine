import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    print(">>> Starting Playwright browser...")
    async with async_playwright() as p:
        # Launch headed chromium to bypass simple bot checks
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(">>> Navigating to Seymour Agency authors page...")
        try:
            await page.goto("https://theseymouragency.com/authors/", wait_until="domcontentloaded", timeout=60000)
            print(">>> Waiting for page to load...")
            await page.wait_for_timeout(10000)  # Wait 10 seconds for rendering
            
            content = await page.content()
            
            output_dir = r"E:\Internship\PocketFM\backend\scratch"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "seymour_page.html")
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
                
            print(f">>> Success! Saved page content to: {output_file}")
            
        except Exception as e:
            print(f"Error during navigation: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
