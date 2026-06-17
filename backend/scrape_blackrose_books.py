import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://www.blackrosewriting.com/romance', wait_until='networkidle')
        
        print("Starting aggressive scrolling...")
        
        previous_count = 0
        unchanged_count = 0
        
        while True:
            # Scroll to the bottom of the page
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)  # Wait for content to load
            
            # Find elements with product titles
            # Squarespace usually uses ProductList-title or similar
            locators = await page.locator('.product-title, .ProductList-title, .sqs-title').all_inner_texts()
            
            # Filter and clean
            current_titles = []
            for text in locators:
                clean_title = text.strip().split('\n')[0]
                if clean_title and clean_title not in current_titles:
                    current_titles.append(clean_title)
                    
            count = len(current_titles)
            print(f"Found {count} books so far...")
            
            if count == previous_count:
                unchanged_count += 1
                if unchanged_count >= 3:
                    print("Reached the end of the list.")
                    break
            else:
                unchanged_count = 0
                previous_count = count

        # Fallback if no titles found using those classes: 
        if count == 0:
            print("Trying generic title extraction...")
            locators = await page.locator('.ProductItem').all()
            # If still nothing, it might be an index page or similar.
        
        print(f"\nFinal count: {len(current_titles)} books")
        
        with open('blackrose_romance_books.txt', 'w', encoding='utf-8') as f:
            for title in current_titles:
                f.write(title + '\n')
                
        print("Saved to blackrose_romance_books.txt")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
