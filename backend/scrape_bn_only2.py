import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

URL = "https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        print(f"Navigating to {URL}")
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Try to accept cookies if banner exists
        try:
            await page.get_by_role("button", name="Accept All Cookies").click(timeout=3000)
            print("Accepted cookies")
        except:
            pass
        
        books = []
        prev_count = 0
        attempts = 0
        
        while True:
            # Scroll to bottom smoothly to trigger any lazy loading
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight - 1000)")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Click load more using Playwright native locators
            try:
                load_more_btn = page.locator("button:has-text('Load More'), button:has-text('Show More'), a:has-text('Load More'), a:has-text('Show More')").first
                if await load_more_btn.is_visible():
                    print("Found 'Load More' button. Clicking natively with Playwright...")
                    await load_more_btn.scroll_into_view_if_needed()
                    await load_more_btn.click(force=True)
                    await page.wait_for_timeout(5000) # wait for new books to load
                    await page.screenshot(path=f"bn_debug_{attempts}.png")
                else:
                    print("No visible 'Load More' button found in DOM.")
            except Exception as e:
                print(f"Error finding/clicking Load More: {e}")
                
            # Extract books
            current_books = await page.evaluate('''() => {
                let items = [];
                let seen = new Set();
                let links = Array.from(document.querySelectorAll('a[href^="/w/"]'));
                
                links.forEach(a => {
                    let title = a.innerText.trim() || a.getAttribute('title');
                    if(!title || title.length < 2) return;
                    if(seen.has(title)) return;
                    seen.add(title);
                    
                    let author = "Unknown";
                    let container = a.closest('div, section, article');
                    if(container) {
                        let authorEl = container.querySelector('a[href^="/authors/"], a[href*="/contributor/"]');
                        if(authorEl) {
                            author = authorEl.innerText.trim();
                        } else {
                            let allLinks = Array.from(document.querySelectorAll('a'));
                            let idx = allLinks.indexOf(a);
                            if(idx > -1) {
                                for(let i=idx+1; i < Math.min(idx+5, allLinks.length); i++) {
                                    let href = allLinks[i].getAttribute('href') || "";
                                    if(href.startsWith('/authors/') || href.includes('/contributor/')) {
                                        author = allLinks[i].innerText.trim();
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    items.push({title: title, author: author});
                });
                return items;
            }''')
            
            books = current_books
            print(f"Gathered {len(books)} books so far...")
            
            if len(books) == prev_count:
                attempts += 1
                if attempts > 3:
                    print("No more new books appearing after 3 attempts. Breaking.")
                    break
            else:
                attempts = 0
                
            prev_count = len(books)
            
            if len(books) >= 1200:
                print("Reached 1200 target!")
                break
                
        print(f"Total books extracted: {len(books)}")
        await browser.close()
        
        if len(books) > 24:
            df = pd.DataFrame([{
                'Name of Series': b['title'],
                'Author Name': b['author'],
                'Publisher': "",
                'GoodReads series link': "",
                'Number of PRIMARY books in the series': 1,
                'Rating (out of 5) of Primary Book 1': "",
                'Ratings (#) of Primary Book 1': "",
                'Synopsis (if available)': "",
                'Romantasy = Yes or No?': "Yes",
                'Romantasy Sub-Genre of series': "",
                'Name of agent in the main folder': ""
            } for b in books])
            
            df.to_excel(r"E:\Internship\PocketFM\Next_Agency.xlsx", index=False)
            print("Saved updated list to Next_Agency.xlsx")

asyncio.run(main())
