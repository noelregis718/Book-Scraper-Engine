import asyncio
import urllib.parse
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        query = "Take It From the Top Claire Swinarski"
        print(f"Searching DuckDuckGo for: {query}")
        
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query + ' site:goodreads.com/book/show')}"
        await page.goto(search_url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        links = await page.query_selector_all('a.result__url')
        if links:
            href = await links[0].get_attribute('href')
            print(f"Found DDG Link: {href}")
            # The href from duckduckgo looks like //duckduckgo.com/l/?uddg=https://www.goodreads.com...
            # We can decode it!
            actual_url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
            print(f"Actual Goodreads URL: {actual_url}")
        else:
            print("No DDG links found.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
