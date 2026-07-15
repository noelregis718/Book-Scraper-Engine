import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        await stealth_async(page)
        
        # Test original B&N URL
        url = "https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance"
        print(f"Navigating to {url}")
        
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Check if books are in DOM
        books = await page.evaluate('''() => {
            let nodes = document.querySelectorAll('a[title], h3 a, div[class*="product-shelf-title"] a');
            return Array.from(nodes).map(n => n.innerText || n.getAttribute('title')).filter(t => t && t.length > 2);
        }''')
        
        print(f"Found {len(books)} potential books. First 5: {books[:5]}")
        
        # Check if 'Show more' button exists
        btns = await page.evaluate('''() => {
            let b = Array.from(document.querySelectorAll('button, a'));
            return b.filter(btn => btn.innerText && (btn.innerText.toLowerCase().includes('show more') || btn.innerText.toLowerCase().includes('load more'))).map(btn => btn.innerText);
        }''')
        
        print(f"Found buttons matching 'show more': {btns}")
        await browser.close()

asyncio.run(main())
