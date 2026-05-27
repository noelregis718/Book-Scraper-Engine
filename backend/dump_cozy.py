import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Run headed to avoid bot detection
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        print("Navigating to cozyromantasy.com...")
        await page.goto("https://www.cozyromantasy.com/")
        print("Waiting for page to load and rendering to complete...")
        await page.wait_for_timeout(5000)
        
        # We need to get all the text that looks like a book title or author.
        # Let's extract all text from paragraph and header elements.
        texts = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('h1, h2, h3, h4, p, span'))
                 .map(el => el.innerText.trim())
                 .filter(t => t.length > 0);
        }''')
        
        print(f"Extracted {len(texts)} text elements.")
        
        with open("cozy_dump.txt", "w", encoding="utf-8") as f:
            for t in texts:
                # Remove newlines inside the text block to make it 1 line per element
                t = t.replace('\n', ' | ')
                f.write(t + "\n")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
