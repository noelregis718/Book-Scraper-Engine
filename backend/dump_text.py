import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.confluencelit.com/authors", timeout=60000)
        
        # Wait for the page to be fully loaded
        await page.wait_for_timeout(5000)
        await page.wait_for_load_state('networkidle')
        
        # Extract the entire visible text from the body
        text = await page.evaluate("document.body.innerText")
        
        # Save to a file so we can analyze it
        with open("body_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        print("Saved visible text to body_text.txt")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
