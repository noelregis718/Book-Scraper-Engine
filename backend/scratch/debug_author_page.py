import asyncio
from playwright.async_api import async_playwright
import os

SAMPLES = [
    "https://theseymouragency.com/author/a-l-jackson/",
    "https://theseymouragency.com/author/abigail-wilson/"
]

async def main():
    print(">>> Starting Playwright browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        output_dir = r"E:\Internship\PocketFM\backend\scratch"
        os.makedirs(output_dir, exist_ok=True)
        
        for idx, url in enumerate(SAMPLES, 1):
            print(f">>> Navigating to sample {idx}: {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(5000)
                
                content = await page.content()
                output_file = os.path.join(output_dir, f"author_sample_{idx}.html")
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  Saved page content to: {output_file}")
                
            except Exception as e:
                print(f"Error loading {url}: {e}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
