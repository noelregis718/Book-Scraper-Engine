import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def check():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        
        url = 'https://theseymouragency.com/author/annette-m-clayton/'
        await page.goto(url, wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)
        
        c = await page.content()
        soup = BeautifulSoup(c, 'html.parser')
        container = soup.find(class_='xixs-related-books')
        if container:
            print("=== Found related books container ===")
            book_divs = container.find_all(class_='xixs-related-book')
            print(f"Found {len(book_divs)} books.")
            for idx, div in enumerate(book_divs, 1):
                print(f"\n--- Book {idx} ---")
                print(div.prettify()[:1000])
        else:
            print("Container not found!")
            
        await b.close()

asyncio.run(check())
