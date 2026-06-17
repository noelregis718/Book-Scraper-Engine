import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.blackrosewriting.com/romance', wait_until='networkidle')
        
        # Give it a moment to load
        await asyncio.sleep(2)
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for product titles
        titles = []
        for elem in soup.find_all(class_=lambda c: c and ('title' in c.lower() or 'product' in c.lower())):
            text = elem.text.strip()
            if text and len(text) < 100:
                titles.append(text)
        
        print("Found classes with 'title' or 'product':")
        for t in list(set(titles))[:20]:
            print("-", t)
            
        print("\nChecking for pagination or next buttons:")
        for elem in soup.find_all('a'):
            if 'next' in elem.text.lower() or 'older' in elem.text.lower() or 'load more' in elem.text.lower():
                print("Pagination link:", elem.text.strip(), elem.get('href'))
                
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
