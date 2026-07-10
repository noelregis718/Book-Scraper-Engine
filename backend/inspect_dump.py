import asyncio
import re
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        print("Navigating...")
        await page.goto('https://harpercollins.co.uk/collections/romantasy', wait_until='networkidle')
        await asyncio.sleep(2)
        
        # Accept cookies
        try:
            accept_btn = page.locator("button:has-text('Accept'), button#onetrust-accept-btn-handler")
            if await accept_btn.is_visible():
                await accept_btn.click()
                await asyncio.sleep(1)
        except: pass

        # Load all pages by clicking Load More if it exists, or just scrolling
        for i in range(15):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            
            # Check for generic pagination next button and click it to load next chunk on the same page
            try:
                load_more = page.locator("a.next:not([class*='swiper']), a.load-more, button:has-text('Load More'), span.next a")
                if await load_more.is_visible():
                    await load_more.click()
                    await asyncio.sleep(2)
            except: pass

        html = await page.content()
        with open('e:/Internship/PocketFM/backend/harper_scroll_dump.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        products = await page.query_selector_all("h5 a, h3 a, h2 a, a.product-card__title, .product-item__title a")
        titles = [await p.inner_text() for p in products]
        print(f"Found {len(titles)} potential titles.")
        for t in titles[:20]:
            if len(t.strip()) > 2: print(t.strip())
            
        await b.close()

asyncio.run(run())
