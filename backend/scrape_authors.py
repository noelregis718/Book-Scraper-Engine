import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Starting browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to URL...")
        await page.goto("https://www.confluencelit.com/authors", timeout=60000)
        
        print("Waiting for network idle...")
        await page.wait_for_timeout(3000)
        
        # Squarespace gallery or portfolio grids typically use h1/h2/h3 or specific classes
        print("Extracting elements...")
        elements = await page.evaluate('''() => {
            // Try to find common Squarespace item titles
            let nodes = document.querySelectorAll('h1, h2, h3, .portfolio-title, .summary-title, .sqs-title');
            let results = [];
            for (let node of nodes) {
                let text = node.innerText.trim();
                if (text && text.length > 2) {
                    results.push({tag: node.tagName, text: text, className: node.className});
                }
            }
            return results;
        }''')
        
        print(f"Found {len(elements)} potential author elements.")
        for el in elements:
            print(f"[{el['tag']}] {el['text']}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
