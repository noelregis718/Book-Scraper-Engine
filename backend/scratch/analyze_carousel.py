import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def analyze_carousel(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"Analyzing {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(4)
        
        # Look for images in the carousel area
        # Often these are in a 'slick-track' or similar container
        titles = await page.evaluate("""() => {
            const results = [];
            // Target images inside common slider containers
            const images = document.querySelectorAll('img');
            images.forEach(img => {
                const alt = img.alt || '';
                const src = img.src || '';
                // Heuristic: book covers usually have 'cover' or 'book' in src, or are in a specific div
                if (alt.length > 3 && !alt.includes('SBR') && !alt.includes('Agent')) {
                    results.push(alt);
                }
            });
            return results;
        }""")
        
        print(f"Found potential titles: {titles}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_carousel("https://sbrmedia.com/authors/a-m-hargrove/"))
