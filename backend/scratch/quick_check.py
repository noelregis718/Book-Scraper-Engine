import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def check():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        
        print("--- Without route aborting ---")
        await page.goto('https://theseymouragency.com/author/a-l-jackson/', wait_until='commit')
        await page.wait_for_timeout(3000)
        c = await page.content()
        soup = BeautifulSoup(c, 'html.parser')
        h = soup.find(class_='xixs-related-books-section-title')
        print('Heading found:', h)
        if h:
            container = soup.find(class_='xixs-related-books')
            print('Container found:', container is not None)
            if container:
                print('Img count:', len(container.find_all('img')))
                for img in container.find_all('img')[:3]:
                    print("  src:", img.get("src"))
                    
        print("\n--- With route aborting ---")
        page2 = await b.new_page()
        await page2.route("**/*.{png,jpg,jpeg,gif,webp,css,woff,woff2,svg}", lambda route: route.abort())
        await page2.goto('https://theseymouragency.com/author/a-l-jackson/', wait_until='commit')
        await page2.wait_for_timeout(3000)
        c2 = await page2.content()
        soup2 = BeautifulSoup(c2, 'html.parser')
        h2 = soup2.find(class_='xixs-related-books-section-title')
        print('Heading found with abort:', h2)
        if h2:
            container2 = soup2.find(class_='xixs-related-books')
            print('Container found with abort:', container2 is not None)
            if container2:
                print('Img count with abort:', len(container2.find_all('img')))
                for img in container2.find_all('img')[:3]:
                    print("  src with abort:", img.get("src"))
        await b.close()

asyncio.run(check())
