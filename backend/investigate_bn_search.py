import asyncio
from playwright.async_api import async_playwright

async def investigate():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        url = "https://www.barnesandnoble.com/s/fantasy+romance"
        print(f"Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)
            
            # Sort by bestsellers
            try:
                await page.evaluate('''() => {
                    let sortBtn = document.querySelector('select#sortMenu');
                    if(sortBtn) {
                        sortBtn.value = "Best Sellers";
                        sortBtn.dispatchEvent(new Event('change'));
                    }
                }''')
                await page.wait_for_timeout(3000)
            except:
                print("Could not sort")
                
            html = await page.content()
            with open("bn_search_dump.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved DOM to bn_search_dump.html")
            
        except Exception as e:
            print(f"Error: {e}")
            
        await browser.close()

asyncio.run(investigate())
