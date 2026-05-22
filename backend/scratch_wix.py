import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.madwomanliterary.com/')
        await asyncio.sleep(3)
        text = await page.evaluate('document.body.innerText')
        lines = [line for line in text.split('\n') if line.strip()]
        for idx, line in enumerate(lines):
            print(idx, line.encode('ascii', 'ignore').decode('ascii'))
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
