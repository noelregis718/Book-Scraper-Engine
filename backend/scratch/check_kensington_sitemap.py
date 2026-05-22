import asyncio
import os
from playwright.async_api import async_playwright

async def check_sitemap():
    url = "https://www.kensingtonbooks.com/sitemap.xml"
    async with async_playwright() as p:
        print("[System] Launching browser to check sitemap.xml...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            status = response.status
            print(f"Sitemap.xml status code: {status}")
            title = await page.title()
            print(f"Page Title: '{title}'")
            if status == 200:
                text = await page.evaluate("() => document.body.innerText")
                print("Sitemap Snippet:")
                print(text[:1000])
        except Exception as e:
            print(f"[Error] Failed to read sitemap.xml: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_sitemap())
