import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to URL...")
        await page.goto("https://randomhousebooks.com/imprint/del-rey/", wait_until="networkidle")
        
        # Let's wait a bit for any dynamic content
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for buttons or labels containing "Romantasy"
        print("Searching for Romantasy filter...")
        elements = soup.find_all(lambda tag: tag.string and 'romantasy' in tag.string.lower())
        for el in elements:
            print(f"Found: <{el.name} class='{el.get('class', [])}' id='{el.get('id', '')}'> {el.string.strip()} </{el.name}>")
            parent = el.parent
            if parent:
                print(f"Parent: <{parent.name} class='{parent.get('class', [])}' id='{parent.get('id', '')}'>")

        # Let's also look for inputs or buttons that might be filters
        filters = soup.find_all('input', type='checkbox')
        print(f"Found {len(filters)} checkboxes")
        for f in filters[:5]:
            print(f)
            
        buttons = soup.find_all('button')
        print(f"Found {len(buttons)} buttons")
        for b in buttons:
            if b.string and 'load more' in b.string.lower():
                print(f"Load more button: {b}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
