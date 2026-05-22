import asyncio
from playwright.async_api import async_playwright

async def find_author_position(target_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        authors = []
        current_page = 1
        found_idx = -1
        
        print(f"Searching for '{target_name}' on SBR Media...")
        
        while True:
            url = f"https://sbrmedia.com/authors/page/{current_page}/" if current_page > 1 else "https://sbrmedia.com/authors/"
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(2)
                
                # Extract all author links on current page
                page_authors = await page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a'))
                        .filter(a => a.href.includes('/authors/') && a.href !== 'https://sbrmedia.com/authors/' && a.innerText.trim().length > 2)
                        .map(a => a.innerText.trim());
                }""")
                
                if not page_authors:
                    break
                
                for name in page_authors:
                    if name not in authors:
                        authors.append(name)
                        if name.lower() == target_name.lower():
                            found_idx = len(authors) - 1
                            print(f"Found {target_name} at Index: {found_idx}")
                
                if found_idx != -1:
                    break
                    
                current_page += 1
            except Exception as e:
                print(f"Error on page {current_page}: {e}")
                break
        
        if found_idx != -1:
            print("\nNext 10 authors in line:")
            for i in range(found_idx + 1, min(found_idx + 11, len(authors))):
                print(f"  {i}: {authors[i]}")
        else:
            print(f"\nCould not find {target_name} in the first {len(authors)} authors.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_author_position("Bailey West"))
