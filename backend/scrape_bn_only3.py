import asyncio
import pandas as pd
from playwright.async_api import async_playwright

URL = "https://www.barnesandnoble.com/pages/bestsellers?orderBy=attributes.mfield_bnb__salesRank&attributes.subjectCategoryDisplayName=Fantasy+Romance"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        print(f"Navigating to {URL}")
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        try:
            await page.locator("button:has-text('Accept'), button:has-text('Accept All')").first.click(timeout=3000)
            print("Cookie banner accepted")
        except:
            pass
        
        books = []
        clicks = 0
        MAX_CLICKS = 50
        
        while clicks < MAX_CLICKS:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight - 500)")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            try:
                # Find all potential load more buttons
                load_more = page.locator("button:has-text('Load More'), button:has-text('Show More'), a:has-text('Load More'), a:has-text('Show More')").first
                if await load_more.count() > 0:
                    if await load_more.is_visible():
                        await load_more.evaluate("el => el.click()")
                        clicks += 1
                        print(f"Clicked Load More {clicks}/{MAX_CLICKS} times...", flush=True)
                        await page.wait_for_timeout(5000)
                    else:
                        print("Load More is hidden. Assuming all books are loaded.", flush=True)
                        break
                else:
                    print("No Load More button found in DOM. All books loaded.", flush=True)
                    break
            except Exception as e:
                print(f"Stopped clicking Load More: {e}")
                break
                
            # Quick check if books increased
            current_count = await page.locator('a[href^="/w/"]').count()
            print(f"Books in DOM: {current_count}")
            
            if 'prev_count' not in locals():
                prev_count = 0
                stuck = 0
                
            if current_count == prev_count:
                stuck += 1
                if stuck > 2:
                    print("Count stopped increasing. Reached the end of the list!")
                    break
            else:
                stuck = 0
                
            prev_count = current_count
            
            if current_count >= 1200:
                print("Reached 1200 target!")
                break
                
        print("Extracting book data...", flush=True)
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
        print(f"Total books extracted: {len(books)}")
        await browser.close()
        
        # Save and style Excel
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
        
        file_path = r"E:\Internship\PocketFM\Next_Agency.xlsx"
        df.to_excel(file_path, index=False)
        
        import os
        os.system("python format_next_agency.py")
        print("Saved to Next_Agency.xlsx with premium styling")

asyncio.run(main())
