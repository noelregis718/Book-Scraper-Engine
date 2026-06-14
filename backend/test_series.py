import asyncio
from playwright.async_api import async_playwright
import re

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # A Court of Thorns and Roses (known series)
        await page.goto("https://www.goodreads.com/book/show/10614.A_Court_of_Thorns_and_Roses", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Find all links containing series
        links = await page.query_selector_all('a')
        found_series = False
        for link in links:
            href = await link.get_attribute('href')
            if href and 'series' in href.lower():
                print(f"Found series link candidate: {href}")
                series_link = href
                found_series = True
                break
                
        if not found_series:
            print("Did not find any series links.")
            
        if series_link:
            full_series_link = series_link if series_link.startswith('http') else f"https://www.goodreads.com{series_link}"
            await page.goto(full_series_link, wait_until="domcontentloaded")
            await asyncio.sleep(3)
            
            # Series subtitle
            desc_elem = await page.query_selector('div.responsiveSeriesHeader__subtitle')
            if desc_elem:
                desc = await desc_elem.inner_text()
                print(f"Series desc: {desc}")
                match = re.search(r'(\d+)\s+primary\s+works', desc, re.IGNORECASE)
                if match:
                    print(f"Primary works: {match.group(1)}")
                else:
                    print("Regex match failed.")
            else:
                print("Could not find div.responsiveSeriesHeader__subtitle")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
