import asyncio
from playwright.async_api import async_playwright

async def find_author_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.limaagency.se/authors", wait_until="networkidle")
        
        # Scroll to ensure all content is loaded
        for i in range(5):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)
            
        # Get all links and their text
        links = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.trim(),
                href: a.href,
                role: a.getAttribute('role')
            }));
        }""")
        
        print(f"Total links found: {len(links)}")
        for link in links:
            if link['text'] and len(link['text'].split()) >= 2:
                print(f"Link: {link['text']} | URL: {link['href']}")
                
        # Also check for elements with role="link"
        other_links = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('[role="link"]')).map(a => ({
                text: a.innerText.trim(),
                href: a.getAttribute('href') || a.getAttribute('data-url')
            }));
        }""")
        print(f"\nOther role='link' elements: {len(other_links)}")
        for link in other_links:
             if link['text'] and len(link['text'].split()) >= 2:
                print(f"Role Link: {link['text']} | URL: {link['href']}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_author_links())
