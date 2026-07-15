import asyncio
from playwright.async_api import async_playwright

async def test_bn():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        await page.goto("https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance", wait_until="domcontentloaded")
        content = await page.content()
        with open("bn_dump.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Length:", len(content))
        await browser.close()

asyncio.run(test_bn())
