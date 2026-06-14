import asyncio
from playwright.async_api import async_playwright

async def get_links(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(4)
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 1000);")
            await asyncio.sleep(1)
        links = await page.query_selector_all('a.product-item-link, a')
        hrefs = []
        for l in links:
            h = await l.get_attribute('href')
            if h and '-tp.html' in h:
                hrefs.append(h)
        await browser.close()
        return set(hrefs)

async def main():
    l1 = await get_links("https://www.sourcebooks.com/fiction/romance")
    l2 = await get_links("https://www.sourcebooks.com/fiction/romance?p=2")
    l3 = await get_links("https://www.sourcebooks.com/fiction/romance?page=2")
    
    print("Links on base url:", len(l1))
    print("Links on ?p=2:", len(l2))
    print("Links on ?page=2:", len(l3))
    print("Overlap base & p=2:", len(l1.intersection(l2)))
    print("Overlap base & page=2:", len(l1.intersection(l3)))

if __name__ == "__main__":
    asyncio.run(main())
