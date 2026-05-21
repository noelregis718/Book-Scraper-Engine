"""Quick exploratory inspect of the Mushens all-authors page DOM."""
import asyncio
from playwright.async_api import async_playwright


async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        await page.goto("https://www.mushens-entertainment.com/all-authors",
                        wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2)

        # Try several common patterns
        for sel in [
            'h2, h3, h4',
            '.author-name',
            '[class*="author"]',
            'a[href*="/author"]',
            'a[href*="/authors/"]',
            'article',
            '.team-member',
            '.grid-item',
            'h2 a, h3 a, h4 a',
        ]:
            els = await page.query_selector_all(sel)
            print(f'Selector {sel!r}: {len(els)} matches')

        print('\n--- First 30 h2/h3/h4 texts ---')
        els = await page.query_selector_all('h2, h3, h4')
        for el in els[:30]:
            t = (await el.inner_text()).strip()
            if t:
                print('  ', repr(t[:80]))

        print('\n--- All links containing "author" ---')
        links = await page.query_selector_all('a[href*="author"]')
        print(f'  Count: {len(links)}')
        for el in links[:20]:
            h = await el.evaluate("el => el.href")
            t = (await el.inner_text()).strip()
            print(f'  {t!r:50} -> {h}')

        # Dump full text length and a snippet
        body_text = await page.inner_text("body")
        print(f'\nbody text length: {len(body_text)}')
        print('First 800 chars:')
        print(body_text[:800])

        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect())
