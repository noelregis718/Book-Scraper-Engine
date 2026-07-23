import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://www.goodreads.com/book/show/243114685-rejected-mate"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        
        # Get all <p> elements
        ps = await page.query_selector_all('p')
        for p_el in ps:
            text = await p_el.inner_text()
            if 'Published' in text:
                print("FOUND P:", text)
                
        # Get all <div> elements containing "Published"
        divs = await page.query_selector_all('div')
        for div_el in divs:
            text = await div_el.inner_text()
            if 'Published' in text and len(text) < 100:
                print("FOUND DIV:", text)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
