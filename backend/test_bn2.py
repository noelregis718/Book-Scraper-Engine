import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def test_bn():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        print("Navigating...")
        await page.goto("https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance", wait_until="networkidle", timeout=60000)
        
        # Wait a bit more for React to render
        await page.wait_for_timeout(5000)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Try to find common B&N book selectors
        products = soup.find_all('div', class_=lambda c: c and ('product' in c.lower() or 'item' in c.lower()))
        print(f"Found {len(products)} potential product divs")
        
        # Print text to a file
        text = soup.get_text(separator='\n', strip=True)
        with open('bn_text.txt', 'w', encoding='utf-8') as f:
            f.write(text)
            
        # Let's take a screenshot to see what it looks like
        await page.screenshot(path="bn_screenshot.png")
        print("Done. Saved text to bn_text.txt and screenshot to bn_screenshot.png")
        
        await browser.close()

asyncio.run(test_bn())
