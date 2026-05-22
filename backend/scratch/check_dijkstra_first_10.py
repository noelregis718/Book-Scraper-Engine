import asyncio
from playwright.async_api import async_playwright

async def check_first_10():
    url = "https://dijkstraagency.com/books-by-subject.php?subject1=Romance"
    print(f"Checking first 10 authors from: {url}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(url)
        # Wait for the containers to load
        await page.wait_for_selector('.books-by-subject-wrap')
        
        wraps = await page.query_selector_all('.books-by-subject-wrap')
        count = 0
        for wrap in wraps:
            if count >= 10: break
            
            # Title Extraction
            title_el = await wrap.query_selector('.book_title_list')
            if not title_el:
                title_el = await wrap.query_selector('a[href*="book-page.php"]')
            
            if not title_el: continue
            title = (await title_el.inner_text()).strip()
            if not title: continue
            
            # Author Extraction (Using the fixed logic)
            author_el = await wrap.query_selector('a[href*="author-page.php"]')
            author = "Unknown"
            if author_el:
                author = (await author_el.inner_text()).strip()
            else:
                # Fallback: check p tags for "By"
                ps = await wrap.query_selector_all('p')
                for p in ps:
                    p_text = await p.inner_text()
                    if "By" in p_text:
                        author = p_text.replace("By", "").strip()
                        break
            
            print(f"{count+1}. Title: {title}")
            print(f"   Author: {author}\n")
            count += 1
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_first_10())
