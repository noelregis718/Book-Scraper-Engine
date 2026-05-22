import asyncio
import os
from playwright.async_api import async_playwright

async def read_robots():
    url = "https://www.kensingtonbooks.com/robots.txt"
    async with async_playwright() as p:
        print("[System] Launching browser to read robots.txt...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            text = await page.evaluate("() => document.body.innerText")
            print("Robots.txt Content:")
            print("-" * 40)
            print(text)
            print("-" * 40)
        except Exception as e:
            print(f"[Error] Failed to read robots.txt: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(read_robots())
