import asyncio
from playwright.async_api import async_playwright
import os

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Visiting Authors page...")
        await page.goto('https://www.stormliteraryagency.com/authors.html', wait_until='domcontentloaded')
        
        # Let's see the structure by pulling all paragraph or heading texts
        content = await page.evaluate('''() => {
            let elements = document.querySelectorAll('p, h1, h2, h3, h4, a, span');
            let results = [];
            for (let el of elements) {
                if (el.innerText && el.innerText.trim() !== '') {
                    results.push(el.tagName + ": " + el.innerText.trim());
                }
            }
            return results;
        }''')
        
        print("Body content overview:")
        for line in content[:50]:
            print(line)
            
        print("\n\nLet's extract links that are NOT in the nav:")
        links = await page.evaluate('''() => {
            let a_tags = document.querySelectorAll('div:not([class*="nav"]) a');
            return Array.from(a_tags).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }));
        }''')
        
        for l in links[:20]:
            if l['text']:
                print(f"  - {l['text']}: {l['href']}")
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect())
