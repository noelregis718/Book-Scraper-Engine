import asyncio
from playwright.async_api import async_playwright
import os

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Visiting Authors page...")
        await page.goto('https://www.stormliteraryagency.com/authors.html')
        
        # Get all links that might be authors
        # In many sites, author links are inside a specific container or just all links on the author page.
        # Let's get all a tags and their href and text
        links = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }));
        }''')
        
        # Let's filter links that seem like author links
        author_links = [l for l in links if l['href'] and ('/author' in l['href'].lower() or 'stormliteraryagency.com' in l['href']) and l['text']]
        
        print(f"Found {len(author_links)} potential author links. Sample:")
        for l in author_links[:10]:
            print(f"  - {l['text']}: {l['href']}")
            
        if not author_links:
            # Maybe the authors are just listed differently.
            print("No obvious author links found. Getting body innerText snippet:")
            body_text = await page.evaluate("document.body.innerText")
            print(body_text[:1000])
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect())
