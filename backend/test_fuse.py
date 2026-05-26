import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.fuseliterary.com/our-books/?_book_genre=romance')
        await page.wait_for_timeout(5000)
        
        # Check if load more button exists
        load_more = await page.evaluate('''() => {
            let btns = Array.from(document.querySelectorAll('button, a'));
            let loadBtn = btns.find(b => b.innerText.toLowerCase().includes('load more'));
            return loadBtn ? loadBtn.className : 'Not found';
        }''')
        print(f"Load more class: {load_more}")
        
        # Extract books
        books = await page.evaluate('''() => {
            // Find common book containers
            let titles = Array.from(document.querySelectorAll('h2, h3')).map(e => e.innerText.trim()).filter(t => t.length > 0);
            return titles.slice(0, 20);
        }''')
        print(f"Titles found: {books}")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
