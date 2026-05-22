import asyncio
from playwright.async_api import async_playwright

async def dump_html(url, out):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(5)
        content = await page.content()
        with open(out, "w", encoding="utf-8") as f:
            f.write(content)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump_html("https://sbrmedia.com/authors/a-m-hargrove/", "sbr_hargrove.html"))
