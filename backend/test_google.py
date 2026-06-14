import asyncio
import urllib.parse
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        query = "Take It From the Top Claire Swinarski"
        print(f"Searching Google for: {query}")
        
        search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query + ' site:goodreads.com/book/show')}"
        await page.goto(search_url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        links = await page.query_selector_all('a[href*="goodreads.com/book/show"]')
        if links:
            href = await links[0].get_attribute('href')
            print(f"Found Google Link: {href}")
        else:
            print("No Google links found.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
