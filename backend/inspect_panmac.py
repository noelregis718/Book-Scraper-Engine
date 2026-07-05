import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent='Mozilla/5.0')
        page = await context.new_page()
        await page.goto('https://www.panmacmillan.com.au/book-shop/?category%5B%5D=624', wait_until='domcontentloaded')
        await asyncio.sleep(5)
        
        # Get sections that contain books
        books = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll("h4.book-title, h2.woocommerce-loop-product__title, a")).map(el => {
                let parent = el.closest('section, div.row, div.container, ul');
                return {
                    text: el.innerText.trim(),
                    parentClass: parent ? parent.className : "None"
                };
            }).filter(item => item.text.length > 3);
        }''')
        
        print(f"Total elements found: {len(books)}")
        for i, b in enumerate(books[:30]):
            print(f"{i}: {b['text']} | Parent: {b['parentClass']}")
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
