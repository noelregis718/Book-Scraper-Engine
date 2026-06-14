import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import re

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        query = '"A Court of Thorns and Roses" series site:goodreads.com/series'
        ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
        
        await page.goto(ddg_url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        html = await page.content()
        # Look for 'primary works'
        match = re.search(r'(\d+)\s+primary\s+works?', html, re.IGNORECASE)
        if match:
            print(f"Found via DDG search text: {match.group(1)} primary works")
        else:
            print("Did not find in DDG snippet.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
