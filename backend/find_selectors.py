import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        url = "https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance"
        
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Dump all text nodes or links to see what is rendered
        links = await page.evaluate('''() => {
            let results = [];
            document.querySelectorAll('a').forEach(a => {
                let text = a.innerText.trim();
                if(text.length > 5 && !text.includes('Sign In') && !text.includes('Bestsellers')) {
                    results.push({
                        text: text,
                        className: a.className || '',
                        href: a.getAttribute('href') || ''
                    });
                }
            });
            return results;
        }''')
        
        with open('bn_links.json', 'w', encoding='utf-8') as f:
            json.dump(links, f, indent=2)
            
        print(f"Dumped {len(links)} links to bn_links.json")
        await browser.close()

asyncio.run(main())
