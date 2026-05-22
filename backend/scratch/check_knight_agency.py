import asyncio
from playwright.async_api import async_playwright

async def check_knight_agency():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://knightagency.net/ourbooks/?product_cat=fantasy-romance"
        print(f"Opening {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Extract book elements
        books = await page.query_selector_all('.product')
        print(f"Found {len(books)} books.")
        
        for i, book in enumerate(books[:5]):
            title_el = await book.query_selector('.woocommerce-loop-product__title')
            title = await title_el.inner_text() if title_el else "N/A"
            
            # Often author is in the title or a separate link
            link_el = await book.query_selector('a')
            href = await link_el.evaluate("el => el.href") if link_el else "N/A"
            
            print(f"[{i}] Title: {title} | Link: {href}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_knight_agency())
