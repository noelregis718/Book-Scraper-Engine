import asyncio
from playwright.async_api import async_playwright

async def debug_pagination():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://knightagency.net/ourbooks/?product_cat=romantic-suspense"
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        # Print all links that might be pagination
        links = await page.query_selector_all('a')
        for link in links:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if href and ('page' in href.lower() or 'paged=' in href.lower() or re.match(r'^\d+$', text.strip())):
                print(f"Link: {text.strip()} | Href: {href}")
        
        await browser.close()

if __name__ == "__main__":
    import re
    asyncio.run(debug_pagination())
